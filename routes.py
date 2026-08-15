from flask import Blueprint, request, jsonify
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime, timedelta
import io, random
from .realtime import emit_event
from .providers.sms import SmsProvider
from .providers.payment import PaymentProvider
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from . import db
from .models import User, Driver, Vehicle, Ride, Tariff, Rating, OtpCode, SosAlert, Zone, Cancellation, Payment, DriverWallet, Invoice, CorporateAccount, Partner, Reservation, PromoCode, LoyaltyAccount

api = Blueprint("api", __name__)

def user_dict(u):
    return {"id": u.id, "name": u.name, "phone": u.phone, "role": u.role}

@api.post("/auth/login")
def login():
    data = request.get_json() or {}
    user = User.query.filter_by(phone=data.get("phone")).first()
    if not user or not user.active or not check_password_hash(user.password_hash, data.get("password", "")):
        return jsonify({"error": "Identifiants invalides"}), 401
    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user_dict(user)})

@api.get("/me")
@jwt_required()
def me():
    user = User.query.get(int(get_jwt_identity()))
    return jsonify(user_dict(user))

@api.get("/drivers/available")
@jwt_required()
def available_drivers():
    drivers = Driver.query.filter_by(status="available").order_by(Driver.queue_position).all()
    result = []
    for d in drivers:
        result.append({
            "id": d.id,
            "name": d.user.name,
            "lat": d.lat,
            "lng": d.lng,
            "queue_position": d.queue_position,
            "rating": d.rating,
            "vehicle": {
                "plate": d.vehicle.plate if d.vehicle else None,
                "model": d.vehicle.model if d.vehicle else None,
            }
        })
    return jsonify(result)

@api.post("/rides")
@jwt_required()
def create_ride():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    pickup = data.get("pickup", "").strip()
    destination = data.get("destination", "").strip()
    if not pickup or not destination:
        return jsonify({"error": "Départ et destination sont obligatoires"}), 400

    # MVP: estimation forfaitaire. Le moteur tarifaire sera configurable.
    fare = float(data.get("estimated_fare", 5000))
    ride = Ride(
        passenger_id=user_id,
        pickup=pickup,
        destination=destination,
        estimated_fare=fare,
        status="requested",
    )
    db.session.add(ride)
    db.session.commit()
    return jsonify({
        "id": ride.id,
        "status": ride.status,
        "estimated_fare": ride.estimated_fare,
        "message": "Demande enregistrée. Recherche d'un taxi disponible."
    }), 201

@api.get("/rides/<int:ride_id>")
@jwt_required()
def get_ride(ride_id):
    ride = Ride.query.get_or_404(ride_id)
    return jsonify({
        "id": ride.id,
        "pickup": ride.pickup,
        "destination": ride.destination,
        "status": ride.status,
        "estimated_fare": ride.estimated_fare,
        "final_fare": ride.final_fare,
        "driver": ({
            "id": ride.driver.id,
            "name": ride.driver.user.name,
            "rating": ride.driver.rating,
            "vehicle": ride.driver.vehicle.plate if ride.driver.vehicle else None,
        } if ride.driver else None)
    })

@api.get("/admin/dashboard")
@jwt_required()
def dashboard():
    user = User.query.get(int(get_jwt_identity()))
    if user.role != "admin":
        return jsonify({"error": "Accès interdit"}), 403
    return jsonify({
        "passengers": User.query.filter_by(role="passenger").count(),
        "drivers": User.query.filter_by(role="driver").count(),
        "available_drivers": Driver.query.filter_by(status="available").count(),
        "rides": Ride.query.count(),
        "requested_rides": Ride.query.filter_by(status="requested").count(),
        "completed_rides": Ride.query.filter_by(status="completed").count(),
    })


@api.post("/drivers/status")
@jwt_required()
def driver_status():
    user = User.query.get(int(get_jwt_identity()))
    if user.role != "driver":
        return jsonify({"error": "Accès réservé aux chauffeurs"}), 403
    driver = Driver.query.filter_by(user_id=user.id).first()
    data = request.get_json() or {}
    status = data.get("status")
    if status not in {"available", "offline", "busy"}:
        return jsonify({"error": "Statut invalide"}), 400
    driver.status = status
    if "lat" in data: driver.lat = data["lat"]
    if "lng" in data: driver.lng = data["lng"]
    db.session.commit()
    return jsonify({"status": driver.status, "queue_position": driver.queue_position})

@api.post("/rides/<int:ride_id>/accept")
@jwt_required()
def accept_ride(ride_id):
    user = User.query.get(int(get_jwt_identity()))
    if user.role != "driver":
        return jsonify({"error": "Accès réservé aux chauffeurs"}), 403
    driver = Driver.query.filter_by(user_id=user.id).first()
    ride = Ride.query.get_or_404(ride_id)
    if ride.status != "requested":
        return jsonify({"error": "Course déjà attribuée"}), 409
    ride.driver_id = driver.id
    ride.status = "accepted"
    driver.status = "busy"
    db.session.commit()
    return jsonify({"id": ride.id, "status": ride.status})

@api.post("/rides/<int:ride_id>/start")
@jwt_required()
def start_ride(ride_id):
    user = User.query.get(int(get_jwt_identity()))
    ride = Ride.query.get_or_404(ride_id)
    if not ride.driver or ride.driver.user_id != user.id:
        return jsonify({"error": "Non autorisé"}), 403
    if ride.status != "accepted":
        return jsonify({"error": "La course doit être acceptée"}), 409
    ride.status = "in_progress"
    db.session.commit()
    return jsonify({"id": ride.id, "status": ride.status})

@api.post("/rides/<int:ride_id>/complete")
@jwt_required()
def complete_ride(ride_id):
    user = User.query.get(int(get_jwt_identity()))
    ride = Ride.query.get_or_404(ride_id)
    if not ride.driver or ride.driver.user_id != user.id:
        return jsonify({"error": "Non autorisé"}), 403
    if ride.status != "in_progress":
        return jsonify({"error": "Course non démarrée"}), 409
    data = request.get_json() or {}
    ride.final_fare = float(data.get("final_fare", ride.estimated_fare))
    ride.status = "completed"
    ride.driver.status = "available"
    db.session.commit()
    return jsonify({"id": ride.id, "status": ride.status, "final_fare": ride.final_fare})

@api.get("/drivers/me")
@jwt_required()
def driver_me():
    user = User.query.get(int(get_jwt_identity()))
    if user.role != "driver":
        return jsonify({"error": "Accès réservé aux chauffeurs"}), 403
    driver = Driver.query.filter_by(user_id=user.id).first()
    return jsonify({
        "id": driver.id,
        "name": user.name,
        "status": driver.status,
        "queue_position": driver.queue_position,
        "rating": driver.rating,
        "vehicle": {
            "plate": driver.vehicle.plate if driver.vehicle else None,
            "model": driver.vehicle.model if driver.vehicle else None
        }
    })

@api.get("/rides")
@jwt_required()
def rides():
    user = User.query.get(int(get_jwt_identity()))
    if user.role == "driver":
        driver = Driver.query.filter_by(user_id=user.id).first()
        items = Ride.query.filter(
            (Ride.driver_id == driver.id) | (Ride.status == "requested")
        ).order_by(Ride.created_at.desc()).limit(50).all()
    elif user.role == "admin":
        items = Ride.query.order_by(Ride.created_at.desc()).limit(100).all()
    else:
        items = Ride.query.filter_by(passenger_id=user.id).order_by(Ride.created_at.desc()).limit(50).all()

    return jsonify([{
        "id": r.id, "pickup": r.pickup, "destination": r.destination,
        "status": r.status, "estimated_fare": r.estimated_fare,
        "final_fare": r.final_fare,
        "driver": r.driver.user.name if r.driver else None
    } for r in items])

@api.get("/tariffs")
def tariffs():
    items = Tariff.query.filter_by(active=True).order_by(Tariff.destination).all()
    return jsonify([{"id": t.id, "name": t.name, "destination": t.destination, "price": t.price} for t in items])

@api.post("/admin/tariffs")
@jwt_required()
def add_tariff():
    user = User.query.get(int(get_jwt_identity()))
    if user.role != "admin":
        return jsonify({"error": "Accès interdit"}), 403
    data = request.get_json() or {}
    t = Tariff(
        name=data.get("name", "Forfait"),
        destination=data.get("destination", ""),
        price=float(data.get("price", 0)),
        active=True
    )
    db.session.add(t)
    db.session.commit()
    return jsonify({"id": t.id, "destination": t.destination, "price": t.price}), 201

@api.post("/rides/<int:ride_id>/rating")
@jwt_required()
def rate_ride(ride_id):
    user = User.query.get(int(get_jwt_identity()))
    ride = Ride.query.get_or_404(ride_id)
    if user.id != ride.passenger_id or ride.status != "completed":
        return jsonify({"error": "Notation non autorisée"}), 403
    data = request.get_json() or {}
    score = int(data.get("score", 5))
    if score < 1 or score > 5:
        return jsonify({"error": "Note entre 1 et 5"}), 400
    rating = Rating(
        ride_id=ride.id, passenger_id=user.id, driver_id=ride.driver_id,
        score=score, comment=data.get("comment", "")
    )
    db.session.add(rating)
    db.session.commit()
    return jsonify({"message": "Merci pour votre évaluation"})



@api.post("/admin/assign-next/<int:ride_id>")
@jwt_required()
def assign_next(ride_id):
    user = User.query.get(int(get_jwt_identity()))
    if user.role != "admin":
        return jsonify({"error": "Accès interdit"}), 403
    ride = Ride.query.get_or_404(ride_id)
    driver = Driver.query.filter_by(status="available").order_by(
        Driver.queue_position.asc().nullslast(), Driver.id.asc()
    ).first()
    if not driver:
        return jsonify({"error": "Aucun taxi disponible"}), 409
    ride.driver_id = driver.id
    ride.status = "accepted"
    driver.status = "busy"
    db.session.commit()
    return jsonify({
        "ride_id": ride.id,
        "driver_id": driver.id,
        "driver_name": driver.user.name,
        "status": ride.status
    })


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = radians(lat1), radians(lat2)
    dp = radians(lat2 - lat1)
    dl = radians(lon2 - lon1)
    a = sin(dp/2)**2 + cos(p1) * cos(p2) * sin(dl/2)**2
    return 2 * R * atan2(sqrt(a), sqrt(1-a))

@api.post("/admin/assign-nearest/<int:ride_id>")
@jwt_required()
def assign_nearest(ride_id):
    user = User.query.get(int(get_jwt_identity()))
    if user.role != "admin":
        return jsonify({"error": "Accès interdit"}), 403

    ride = Ride.query.get_or_404(ride_id)
    if ride.status != "requested":
        return jsonify({"error": "Course déjà traitée"}), 409

    data = request.get_json() or {}
    pickup_lat = data.get("lat")
    pickup_lng = data.get("lng")

    drivers = Driver.query.filter_by(status="available").all()
    if not drivers:
        return jsonify({"error": "Aucun taxi disponible"}), 409

    if pickup_lat is None or pickup_lng is None:
        driver = sorted(drivers, key=lambda d: (d.queue_position or 999999, d.id))[0]
        distance = None
    else:
        candidates = [d for d in drivers if d.lat is not None and d.lng is not None]
        if candidates:
            driver = min(
                candidates,
                key=lambda d: haversine_km(float(pickup_lat), float(pickup_lng), d.lat, d.lng)
            )
            distance = round(haversine_km(float(pickup_lat), float(pickup_lng), driver.lat, driver.lng), 2)
        else:
            driver = sorted(drivers, key=lambda d: (d.queue_position or 999999, d.id))[0]
            distance = None

    ride.driver_id = driver.id
    ride.status = "accepted"
    driver.status = "busy"
    db.session.commit()

    return jsonify({
        "ride_id": ride.id,
        "driver_id": driver.id,
        "driver_name": driver.user.name,
        "distance_km": distance,
        "status": ride.status
    })

@api.post("/payments/intents")
@jwt_required()
def payment_intent():
    user = User.query.get(int(get_jwt_identity()))
    data = request.get_json() or {}
    method = data.get("method", "cash")
    amount = float(data.get("amount", 0))
    allowed = {"cash", "wave", "orange_money", "card"}
    if method not in allowed:
        return jsonify({"error": "Moyen de paiement non supporté"}), 400
    reference = f"TS-{user.id}-{int(amount)}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    result = PaymentProvider().create_payment(method, amount, reference)
    return jsonify(result), 201

@api.get("/vehicles/<int:vehicle_id>/qr")
def vehicle_qr(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    return jsonify({
        "vehicle_id": vehicle.id,
        "plate": vehicle.plate,
        "model": vehicle.model,
        "service": "TAXI SENIRAN AIBD",
        "qr_payload": f"taxiseniran://vehicle/{vehicle.id}"
    })


@api.post("/auth/request-otp")
def request_otp():
    data = request.get_json() or {}
    phone = (data.get("phone") or "").strip()
    if not phone:
        return jsonify({"error": "Téléphone obligatoire"}), 400
    code = f"{random.randint(0, 999999):06d}"
    otp = OtpCode(phone=phone, code=code, expires_at=datetime.utcnow()+timedelta(minutes=5))
    db.session.add(otp)
    db.session.commit()

    message = f"Votre code TAXI SENIRAN AIBD est {code}. Valable 5 minutes."
    result = SmsProvider().send(phone, message)

    response = {"message": "OTP demandé", "expires_in": 300, "delivery": result}
    if result.get("mode") == "demo":
        response["demo_code"] = code
    return jsonify(response)

@api.post("/auth/verify-otp")
def verify_otp():
    data = request.get_json() or {}
    phone = (data.get("phone") or "").strip()
    code = (data.get("code") or "").strip()
    otp = OtpCode.query.filter_by(
        phone=phone, code=code, used=False
    ).order_by(OtpCode.id.desc()).first()
    if not otp or otp.expires_at < datetime.utcnow():
        return jsonify({"error": "OTP invalide ou expiré"}), 401

    user = User.query.filter_by(phone=phone).first()
    if not user:
        return jsonify({
            "error": "Compte inexistant. Contactez l'administrateur de TAXI SENIRAN AIBD."
        }), 403
    if not user.active:
        return jsonify({"error": "Compte désactivé."}), 403

    otp.used = True
    db.session.commit()
    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user_dict(user)})


@api.post("/drivers/location")
@jwt_required()
def driver_location_realtime():
    user = User.query.get(int(get_jwt_identity()))
    if user.role != "driver":
        return jsonify({"error": "Accès réservé aux chauffeurs"}), 403
    driver = Driver.query.filter_by(user_id=user.id).first()
    data = request.get_json() or {}
    if data.get("lat") is None or data.get("lng") is None:
        return jsonify({"error": "Latitude et longitude obligatoires"}), 400
    driver.lat = float(data["lat"])
    driver.lng = float(data["lng"])
    db.session.commit()
    payload = {"driver_id": driver.id, "lat": driver.lat, "lng": driver.lng, "status": driver.status}
    emit_event("driver_location", payload)
    return jsonify(payload)

@api.post("/sos")
@jwt_required()
def create_sos():
    user = User.query.get(int(get_jwt_identity()))
    data = request.get_json() or {}
    alert = SosAlert(
        ride_id=data.get("ride_id"),
        user_id=user.id,
        lat=data.get("lat"),
        lng=data.get("lng"),
        status="open"
    )
    db.session.add(alert)
    db.session.commit()
    payload = {
        "id": alert.id,
        "ride_id": alert.ride_id,
        "user_id": alert.user_id,
        "lat": alert.lat,
        "lng": alert.lng,
        "status": alert.status
    }
    emit_event("sos_alert", payload)
    return jsonify(payload), 201

@api.get("/admin/sos")
@jwt_required()
def list_sos():
    user = User.query.get(int(get_jwt_identity()))
    if user.role != "admin":
        return jsonify({"error": "Accès interdit"}), 403
    alerts = SosAlert.query.order_by(SosAlert.created_at.desc()).limit(100).all()
    return jsonify([{
        "id": a.id, "ride_id": a.ride_id, "user_id": a.user_id,
        "lat": a.lat, "lng": a.lng, "status": a.status,
        "created_at": a.created_at.isoformat()
    } for a in alerts])

@api.get("/vehicles/<int:vehicle_id>/qr.png")
def vehicle_qr_png(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    import qrcode
    payload = f"taxiseniran://vehicle/{vehicle.id}"
    img = qrcode.make(payload)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    from flask import send_file
    return send_file(buf, mimetype="image/png", download_name=f"taxi_{vehicle.id}_qr.png")


@api.get("/health")
def health():
    return jsonify({"status": "ok", "service": "taxi-seniran-aibd"})

@api.post("/admin/audit")
@jwt_required()
def audit_event():
    user = User.query.get(int(get_jwt_identity()))
    if user.role != "admin":
        return jsonify({"error": "Accès interdit"}), 403
    data = request.get_json() or {}
    # MVP: acknowledge the event. In production store in immutable audit storage.
    return jsonify({
        "accepted": True,
        "actor_id": user.id,
        "event": data.get("event"),
        "resource": data.get("resource")
    }), 201

@api.post("/payments/webhook")
def payment_webhook():
    # Production contract point: verify provider signature before accepting events.
    data = request.get_json() or {}
    return jsonify({
        "received": True,
        "provider": data.get("provider"),
        "reference": data.get("reference")
    })


@api.get("/zones")
def zones():
    return jsonify([{
        "id": z.id, "name": z.name, "latitude": z.latitude,
        "longitude": z.longitude, "radius_m": z.radius_m
    } for z in Zone.query.filter_by(active=True).all()])

@api.post("/admin/zones")
@jwt_required()
def create_zone():
    user=User.query.get(int(get_jwt_identity()))
    if user.role!="admin":
        return jsonify({"error":"Accès interdit"}),403
    data=request.get_json() or {}
    z=Zone(name=data.get("name","Zone"), latitude=float(data["latitude"]),
           longitude=float(data["longitude"]), radius_m=float(data.get("radius_m",1000)))
    db.session.add(z); db.session.commit()
    return jsonify({"id":z.id,"name":z.name}),201

@api.get("/admin/fleet")
@jwt_required()
def fleet():
    user=User.query.get(int(get_jwt_identity()))
    if user.role!="admin":
        return jsonify({"error":"Accès interdit"}),403
    drivers=Driver.query.order_by(Driver.queue_position.asc().nullslast(),Driver.id.asc()).all()
    return jsonify([{
        "driver_id":d.id,
        "name":d.user.name,
        "phone":d.user.phone,
        "status":d.status,
        "queue_position":d.queue_position,
        "lat":d.lat,"lng":d.lng,
        "rating":d.rating,
        "vehicle": {
            "id":d.vehicle.id if d.vehicle else None,
            "plate":d.vehicle.plate if d.vehicle else None,
            "model":d.vehicle.model if d.vehicle else None,
            "active":d.vehicle.active if d.vehicle else False
        }
    } for d in drivers])

@api.post("/admin/drivers/<int:driver_id>/queue")
@jwt_required()
def update_queue(driver_id):
    user=User.query.get(int(get_jwt_identity()))
    if user.role!="admin":
        return jsonify({"error":"Accès interdit"}),403
    d=Driver.query.get_or_404(driver_id)
    pos=int((request.get_json() or {}).get("position",1))
    d.queue_position=max(1,pos)
    db.session.commit()
    return jsonify({"driver_id":d.id,"queue_position":d.queue_position})

@api.post("/rides/<int:ride_id>/cancel")
@jwt_required()
def cancel_ride(ride_id):
    user=User.query.get(int(get_jwt_identity()))
    ride=Ride.query.get_or_404(ride_id)
    if user.id!=ride.passenger_id and (not ride.driver or ride.driver.user_id!=user.id) and user.role!="admin":
        return jsonify({"error":"Non autorisé"}),403
    if ride.status in {"completed","cancelled"}:
        return jsonify({"error":"Course déjà clôturée"}),409
    data=request.get_json() or {}
    reason=data.get("reason","Annulation")
    if ride.driver:
        ride.driver.status="available"
    ride.status="cancelled"
    db.session.add(Cancellation(ride_id=ride.id,user_id=user.id,reason=reason))
    db.session.commit()
    emit_event("ride_cancelled",{"ride_id":ride.id,"reason":reason})
    return jsonify({"id":ride.id,"status":ride.status}),200

@api.get("/admin/kpis")
@jwt_required()
def kpis():
    user=User.query.get(int(get_jwt_identity()))
    if user.role!="admin":
        return jsonify({"error":"Accès interdit"}),403
    total=Ride.query.count()
    completed=Ride.query.filter_by(status="completed").count()
    cancelled=Ride.query.filter_by(status="cancelled").count()
    requested=Ride.query.filter_by(status="requested").count()
    return jsonify({
        "total_rides":total,
        "completed":completed,
        "cancelled":cancelled,
        "requested":requested,
        "completion_rate": round((completed/total)*100,2) if total else 0,
        "cancellation_rate": round((cancelled/total)*100,2) if total else 0
    })


@api.post("/rides/<int:ride_id>/payment")
@jwt_required()
def create_ride_payment(ride_id):
    user=User.query.get(int(get_jwt_identity()))
    ride=Ride.query.get_or_404(ride_id)
    if ride.passenger_id != user.id:
        return jsonify({"error":"Non autorisé"}),403
    if ride.status != "completed":
        return jsonify({"error":"La course doit être terminée"}),409
    data=request.get_json() or {}
    method=data.get("method","cash")
    amount=float(ride.final_fare or ride.estimated_fare or 0)
    reference=f"PAY-{ride.id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
    payment=Payment(
        ride_id=ride.id, passenger_id=user.id, method=method,
        amount=amount, status="pending", reference=reference
    )
    db.session.add(payment)
    db.session.commit()
    return jsonify({
        "id":payment.id,"reference":payment.reference,
        "method":payment.method,"amount":payment.amount,
        "status":payment.status
    }),201

@api.post("/admin/settle-payment/<int:payment_id>")
@jwt_required()
def settle_payment(payment_id):
    user=User.query.get(int(get_jwt_identity()))
    if user.role!="admin":
        return jsonify({"error":"Accès interdit"}),403
    payment=Payment.query.get_or_404(payment_id)
    if payment.status=="paid":
        return jsonify({"error":"Paiement déjà réglé"}),409

    commission_rate=float((request.get_json() or {}).get("commission_rate",0.10))
    commission=round(payment.amount*commission_rate,2)
    driver=payment.ride.driver
    wallet=DriverWallet.query.filter_by(driver_id=driver.id).first()
    if not wallet:
        wallet=DriverWallet(driver_id=driver.id)
        db.session.add(wallet)

    wallet.total_earned += payment.amount
    wallet.total_commission += commission
    wallet.balance += payment.amount-commission
    payment.status="paid"

    invoice=Invoice(
        ride_id=payment.ride_id,
        number=f"INV-{payment.ride_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        subtotal=payment.amount,
        commission=commission,
        total=payment.amount
    )
    db.session.add(invoice)
    db.session.commit()
    return jsonify({
        "payment_id":payment.id,
        "status":payment.status,
        "commission":commission,
        "driver_net":payment.amount-commission,
        "invoice_number":invoice.number
    })

@api.get("/drivers/wallet")
@jwt_required()
def driver_wallet():
    user=User.query.get(int(get_jwt_identity()))
    if user.role!="driver":
        return jsonify({"error":"Accès réservé aux chauffeurs"}),403
    driver=Driver.query.filter_by(user_id=user.id).first()
    wallet=DriverWallet.query.filter_by(driver_id=driver.id).first()
    if not wallet:
        wallet=DriverWallet(driver_id=driver.id)
        db.session.add(wallet); db.session.commit()
    return jsonify({
        "balance":wallet.balance,
        "total_earned":wallet.total_earned,
        "total_commission":wallet.total_commission
    })

@api.get("/admin/finance")
@jwt_required()
def finance():
    user=User.query.get(int(get_jwt_identity()))
    if user.role!="admin":
        return jsonify({"error":"Accès interdit"}),403
    payments=Payment.query.all()
    paid=[p for p in payments if p.status=="paid"]
    revenue=round(sum(p.amount for p in paid),2)
    commission=round(sum(i.commission for i in Invoice.query.all()),2)
    return jsonify({
        "payments_total":len(payments),
        "payments_paid":len(paid),
        "gross_revenue":revenue,
        "commission_revenue":commission,
        "driver_net":round(revenue-commission,2)
    })


@api.get("/corporate")
@jwt_required()
def corporate_accounts():
    user=User.query.get(int(get_jwt_identity()))
    if user.role!="admin":
        return jsonify({"error":"Accès interdit"}),403
    return jsonify([{
        "id":c.id,"company_name":c.company_name,
        "contact_phone":c.contact_phone,
        "credit_limit":c.credit_limit,"balance":c.balance,"active":c.active
    } for c in CorporateAccount.query.order_by(CorporateAccount.company_name).all()])

@api.post("/admin/corporate")
@jwt_required()
def create_corporate():
    user=User.query.get(int(get_jwt_identity()))
    if user.role!="admin":
        return jsonify({"error":"Accès interdit"}),403
    data=request.get_json() or {}
    c=CorporateAccount(
        company_name=data.get("company_name","Entreprise"),
        contact_phone=data.get("contact_phone"),
        credit_limit=float(data.get("credit_limit",0))
    )
    db.session.add(c); db.session.commit()
    return jsonify({"id":c.id,"company_name":c.company_name}),201


@api.post("/reservations")
@jwt_required()
def create_reservation():
    user=User.query.get(int(get_jwt_identity()))
    data=request.get_json() or {}
    try:
        scheduled=datetime.fromisoformat(data["scheduled_at"])
    except Exception:
        return jsonify({"error":"scheduled_at doit être au format ISO"}),400
    if scheduled <= datetime.utcnow():
        return jsonify({"error":"La réservation doit être future"}),400
    reservation=Reservation(
        passenger_id=user.id,
        pickup=data.get("pickup","").strip(),
        destination=data.get("destination","").strip(),
        scheduled_at=scheduled,
        estimated_fare=float(data.get("estimated_fare",5000)),
        partner_id=data.get("partner_id")
    )
    if not reservation.pickup or not reservation.destination:
        return jsonify({"error":"Départ et destination obligatoires"}),400
    db.session.add(reservation); db.session.commit()
    emit_event("reservation_created",{"id":reservation.id,"scheduled_at":scheduled.isoformat()})
    return jsonify({"id":reservation.id,"status":reservation.status}),201

@api.get("/reservations")
@jwt_required()
def reservations():
    user=User.query.get(int(get_jwt_identity()))
    if user.role=="admin":
        items=Reservation.query.order_by(Reservation.scheduled_at.desc()).limit(200).all()
    else:
        items=Reservation.query.filter_by(passenger_id=user.id).order_by(Reservation.scheduled_at.desc()).limit(50).all()
    return jsonify([{
        "id":x.id,"pickup":x.pickup,"destination":x.destination,
        "scheduled_at":x.scheduled_at.isoformat(),"status":x.status,
        "estimated_fare":x.estimated_fare
    } for x in items])

@api.post("/admin/partners")
@jwt_required()
def create_partner():
    user=User.query.get(int(get_jwt_identity()))
    if user.role!="admin": return jsonify({"error":"Accès interdit"}),403
    d=request.get_json() or {}
    p=Partner(name=d.get("name","Partenaire"),partner_type=d.get("partner_type","hotel"),
              phone=d.get("phone"),email=d.get("email"))
    db.session.add(p); db.session.commit()
    return jsonify({"id":p.id,"name":p.name}),201

@api.get("/partners")
def partners():
    return jsonify([{"id":p.id,"name":p.name,"type":p.partner_type} for p in Partner.query.filter_by(active=True).all()])

@api.post("/admin/promos")
@jwt_required()
def create_promo():
    user=User.query.get(int(get_jwt_identity()))
    if user.role!="admin": return jsonify({"error":"Accès interdit"}),403
    d=request.get_json() or {}
    code=d.get("code","").upper().strip()
    if not code: return jsonify({"error":"Code obligatoire"}),400
    promo=PromoCode(code=code,percent=float(d.get("percent",0)),max_uses=int(d.get("max_uses",100)))
    db.session.add(promo); db.session.commit()
    return jsonify({"id":promo.id,"code":promo.code}),201

@api.post("/promos/validate")
def validate_promo():
    d=request.get_json() or {}
    promo=PromoCode.query.filter_by(code=(d.get("code","").upper().strip()),active=True).first()
    if not promo or promo.uses>=promo.max_uses:
        return jsonify({"valid":False,"discount":0})
    amount=float(d.get("amount",0))
    discount=round(amount*promo.percent/100,2)
    return jsonify({"valid":True,"percent":promo.percent,"discount":discount,"final_amount":max(0,amount-discount)})

@api.get("/loyalty")
@jwt_required()
def loyalty():
    uid=int(get_jwt_identity())
    account=LoyaltyAccount.query.filter_by(user_id=uid).first()
    if not account:
        account=LoyaltyAccount(user_id=uid); db.session.add(account); db.session.commit()
    return jsonify({"points":account.points,"level":account.level})

@api.post("/admin/loyalty/credit")
@jwt_required()
def credit_loyalty():
    user=User.query.get(int(get_jwt_identity()))
    if user.role!="admin": return jsonify({"error":"Accès interdit"}),403
    d=request.get_json() or {}
    account=LoyaltyAccount.query.filter_by(user_id=int(d["user_id"])).first()
    if not account:
        account=LoyaltyAccount(user_id=int(d["user_id"])); db.session.add(account)
    account.points += int(d.get("points",0))
    if account.points>=1000: account.level="Premium"
    elif account.points>=500: account.level="Silver"
    db.session.commit()
    return jsonify({"points":account.points,"level":account.level})

@api.post("/admin/users")
@jwt_required()
def admin_create_user():
    owner = User.query.get(int(get_jwt_identity()))
    if not owner or owner.role != "admin":
        return jsonify({"error": "Accès administrateur requis"}), 403

    data = request.get_json() or {}
    role = data.get("role", "passenger")
    if role not in {"passenger", "driver"}:
        return jsonify({"error": "Rôle invalide"}), 400

    name = (data.get("name") or "").strip()
    phone = (data.get("phone") or "").strip()
    password = data.get("password") or ""
    if not name or not phone or len(password) < 8:
        return jsonify({"error": "Nom, téléphone et mot de passe de 8 caractères minimum obligatoires"}), 400
    if User.query.filter_by(phone=phone).first():
        return jsonify({"error": "Ce numéro existe déjà"}), 409

    user = User(
        name=name, phone=phone,
        password_hash=generate_password_hash(password),
        role=role, active=True
    )
    db.session.add(user)
    db.session.commit()

    if role == "driver":
        db.session.add(Driver(user_id=user.id, status="offline"))
        db.session.commit()

    return jsonify({
        "id": user.id, "name": user.name,
        "phone": user.phone, "role": user.role
    }), 201

@api.get("/admin/users")
@jwt_required()
def admin_users():
    owner = User.query.get(int(get_jwt_identity()))
    if not owner or owner.role != "admin":
        return jsonify({"error": "Accès administrateur requis"}), 403
    return jsonify([{
        "id":u.id, "name":u.name, "phone":u.phone,
        "role":u.role, "active":u.active
    } for u in User.query.order_by(User.created_at.desc()).all()])

@api.post("/admin/users/<int:user_id>/status")
@jwt_required()
def admin_user_status(user_id):
    owner = User.query.get(int(get_jwt_identity()))
    if not owner or owner.role != "admin":
        return jsonify({"error": "Accès administrateur requis"}), 403
    user = User.query.get_or_404(user_id)
    if user.role == "admin":
        return jsonify({"error": "Le compte administrateur principal ne peut pas être désactivé."}), 403
    user.active = bool((request.get_json() or {}).get("active", True))
    db.session.commit()
    return jsonify({"id":user.id, "active":user.active})
