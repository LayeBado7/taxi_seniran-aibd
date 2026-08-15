import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'config.dart';
import 'location_service.dart';
import 'map_page.dart';
import 'sos_service.dart';
import 'realtime_service.dart';
import 'otp_page.dart';
import 'wallet_page.dart';
import 'reservation_page.dart';

void main() => runApp(const TaxiSeniranApp());

class TaxiSeniranApp extends StatelessWidget {
  const TaxiSeniranApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'TAXI SENIRAN AIBD',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFFF5C400)),
        useMaterial3: true,
      ),
      home: const LoginPage(),
    );
  }
}

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});
  @override State<LoginPage> createState() => _LoginPageState();
}
class _LoginPageState extends State<LoginPage> {
  final phone = TextEditingController(text: "+221772222222");
  final password = TextEditingController(text: "passenger123");
  bool loading=false;
  Future<void> requestOtp() async {
    setState(()=>loading=true);
    final r=await http.post(Uri.parse("$apiBaseUrl/auth/request-otp"),
      headers:{"Content-Type":"application/json"},
      body:jsonEncode({"phone":phone.text.trim()}));
    setState(()=>loading=false);
    if(!mounted)return;
    if(r.statusCode==200){
      final result=await Navigator.push(context,MaterialPageRoute(
        builder:(_)=>OtpPage(phone:phone.text.trim())
      ));
      if(result != null && mounted){
        Navigator.pushReplacement(context,MaterialPageRoute(
          builder:(_)=>HomePage(user:result["user"])
        ));
      }
    }else{
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content:Text("Impossible d'envoyer le code OTP."))
      );
    }
  }

  Future<void> login() async {
    setState(()=>loading=true);
    final r=await http.post(Uri.parse("$apiBaseUrl/auth/login"),
      headers: {"Content-Type":"application/json"},
      body: jsonEncode({"phone":phone.text,"password":password.text}));
    setState(()=>loading=false);
    if(r.statusCode==200){
      final data=jsonDecode(r.body);
      final p=await SharedPreferences.getInstance();
      await p.setString("token",data["token"]);
      if(mounted) Navigator.pushReplacement(context,MaterialPageRoute(builder:(_)=> data["user"]["role"] == "driver" ? DriverPage(user:data["user"]) : HomePage(user:data["user"])));
    } else if(mounted) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content:Text("Identifiants invalides")));
    }
  }
  @override Widget build(BuildContext context)=>Scaffold(
    body: SafeArea(child: Padding(
      padding: const EdgeInsets.all(28),
      child: Column(crossAxisAlignment:CrossAxisAlignment.stretch,mainAxisAlignment:MainAxisAlignment.center,children:[
        const Icon(Icons.local_taxi,size:80,color:Color(0xFFF5C400)),
        const Text("TAXI SENIRAN AIBD",textAlign:TextAlign.center,style:TextStyle(fontSize:28,fontWeight:FontWeight.w800)),
        const SizedBox(height:8),
        const Text("Réservez votre taxi à l'aéroport",textAlign:TextAlign.center),
        const SizedBox(height:30),
        TextField(controller:phone,keyboardType:TextInputType.phone,decoration:const InputDecoration(labelText:"Téléphone",prefixIcon:Icon(Icons.phone))),
        const SizedBox(height:8),
        OutlinedButton.icon(
          onPressed:loading?null:requestOtp,
          icon:const Icon(Icons.sms),
          label:const Text("SE CONNECTER PAR SMS / OTP"),
        ),
        const SizedBox(height:8),
        TextField(controller:password,obscureText:true,decoration:const InputDecoration(labelText:"Mot de passe (démo)",prefixIcon:Icon(Icons.lock))),
        const SizedBox(height:20),
        FilledButton(onPressed:loading?null:login,child:Text(loading?"Connexion…":"Se connecter")),
      ]),
    )),
  );
}

class HomePage extends StatefulWidget {
  final Map<String,dynamic> user;
  const HomePage({super.key,required this.user});
  @override State<HomePage> createState()=>_HomePageState();
}
class _HomePageState extends State<HomePage>{
  final pickup=TextEditingController(text:"AIBD — Zone Taxis");
  final destination=TextEditingController();
  bool loading=false;
  Future<void> requestRide() async {
    final p=await SharedPreferences.getInstance();
    final token=p.getString("token");
    setState(()=>loading=true);
    final r=await http.post(Uri.parse("$apiBaseUrl/rides"),
      headers:{"Content-Type":"application/json","Authorization":"Bearer $token"},
      body:jsonEncode({"pickup":pickup.text,"destination":destination.text,"estimated_fare":5000}));
    setState(()=>loading=false);
    if(mounted){
      if(r.statusCode==201){
        final d=jsonDecode(r.body);
        if(mounted){
          Navigator.push(context,MaterialPageRoute(
            builder:(_)=>TrackRidePage(rideId:d["id"]),
          ));
        }
      }else{
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content:Text("Impossible de créer la course")));
      }
    }
  }
  @override Widget build(BuildContext context)=>Scaffold(
    appBar:AppBar(title:const Text("TAXI SENIRAN AIBD"),backgroundColor:const Color(0xFFF5C400)),
    body:ListView(padding:const EdgeInsets.all(20),children:[
      Container(height:230,decoration:BoxDecoration(color:Colors.blueGrey.shade50,borderRadius:BorderRadius.circular(18)),
        child:const Center(child:Icon(Icons.map,size:100,color:Colors.blueGrey))),
      const SizedBox(height:18),
      const Text("Où allez-vous ?",style:TextStyle(fontSize:24,fontWeight:FontWeight.w800)),
      const SizedBox(height:12),
      TextField(controller:pickup,decoration:const InputDecoration(labelText:"Point de départ",prefixIcon:Icon(Icons.my_location))),
      TextField(controller:destination,decoration:const InputDecoration(labelText:"Destination",prefixIcon:Icon(Icons.location_on))),
      const SizedBox(height:18),
      FilledButton.icon(onPressed:loading?null:requestRide,icon:const Icon(Icons.local_taxi),label:Text(loading?"Recherche…":"COMMANDER UN TAXI")),
      const SizedBox(height:14),
      OutlinedButton.icon(
        onPressed:() {
          Navigator.push(context, MaterialPageRoute(
            builder:(_) => const TaxiMapPage(
              latitude: 14.6716,
              longitude: -17.0737,
              title: "AIBD — Zone taxis",
            ),
          ));
        },
        icon:const Icon(Icons.map),
        label:const Text("VOIR LA CARTE AIBD"),
      ),
      const SizedBox(height:14),
      OutlinedButton.icon(
        onPressed:()=>Navigator.push(context,MaterialPageRoute(builder:(_)=>const ReservationPage())),
        icon:const Icon(Icons.calendar_month),
        label:const Text("RÉSERVER POUR PLUS TARD")),
      const SizedBox(height:25),
      Card(child:ListTile(leading:const Icon(Icons.verified),title:const Text("Taxis autorisés AIBD"),subtitle:const Text("Chauffeurs et véhicules identifiés et suivis."))),
    ]),
  );
}



class TrackRidePage extends StatefulWidget {
  final int rideId;
  const TrackRidePage({super.key, required this.rideId});
  @override State<TrackRidePage> createState()=>_TrackRidePageState();
}

class _TrackRidePageState extends State<TrackRidePage>{
  Map<String,dynamic>? ride;
  bool loading=true;

  Future<void> load() async {
    final p=await SharedPreferences.getInstance();
    final t=p.getString("token");
    final r=await http.get(Uri.parse("$apiBaseUrl/rides/$rideId"),
      headers:{"Authorization":"Bearer $t"});
    if(r.statusCode==200) {
      setState(()=>ride=jsonDecode(r.body));
    }
    setState(()=>loading=false);
  }

  @override void initState(){super.initState();load();}

  @override Widget build(BuildContext context){
    final r=ride;
    return Scaffold(
      appBar:AppBar(
        title:Text("Course #$rideId"),
        backgroundColor:const Color(0xFFF5C400),
      ),
      body: loading
        ? const Center(child:CircularProgressIndicator())
        : RefreshIndicator(
          onRefresh:load,
          child:ListView(padding:const EdgeInsets.all(18),children:[
            Container(
              height:260,
              decoration:BoxDecoration(
                borderRadius:BorderRadius.circular(20),
                color:const Color(0xFFE9EEF4),
              ),
              child:const Center(
                child:Column(
                  mainAxisAlignment:MainAxisAlignment.center,
                  children:[
                    Icon(Icons.location_on,size:70,color:Color(0xFF143B70)),
                    SizedBox(height:10),
                    Text("Suivi GPS de la course",style:TextStyle(fontSize:18,fontWeight:FontWeight.w700)),
                    Text("La carte interactive sera branchée en production.")
                  ],
                ),
              ),
            ),
            const SizedBox(height:18),
            Text(r?["status"]?.toString().toUpperCase() ?? "INCONNU",
              style:const TextStyle(fontSize:22,fontWeight:FontWeight.w800)),
            const SizedBox(height:10),
            Card(child:ListTile(
              leading:const Icon(Icons.trip_origin),
              title:Text(r?["pickup"] ?? ""),
              subtitle:const Text("Départ"),
            )),
            Card(child:ListTile(
              leading:const Icon(Icons.flag),
              title:Text(r?["destination"] ?? ""),
              subtitle:const Text("Destination"),
            )),
            if(r?["driver"] != null)
              Card(child:ListTile(
                leading:const CircleAvatar(child:Icon(Icons.person)),
                title:Text(r!["driver"]["name"] ?? "Chauffeur"),
                subtitle:Text("Véhicule : ${r["driver"]["vehicle"] ?? "—"}"),
              )),
            Card(child:ListTile(
              leading:const Icon(Icons.payments),
              title:Text("${r?["final_fare"] ?? r?["estimated_fare"] ?? 0} FCFA"),
              subtitle:const Text("Montant"),
            )),
            const SizedBox(height:12),
            const SizedBox(height:10),
            OutlinedButton.icon(
              onPressed:() async {
                final p=await SharedPreferences.getInstance();
                final t=p.getString("token");
                final rr=await http.post(
                  Uri.parse("$apiBaseUrl/rides/${widget.rideId}/cancel"),
                  headers:{"Content-Type":"application/json","Authorization":"Bearer $t"},
                  body:jsonEncode({"reason":"Annulation par le passager"}),
                );
                if(context.mounted && rr.statusCode<300){
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content:Text("Course annulée."))
                  );
                  await load();
                }
              },
              icon:const Icon(Icons.cancel_outlined),
              label:const Text("Annuler la course"),
            ),
            FilledButton.icon(
              style:FilledButton.styleFrom(backgroundColor:Colors.red),
              onPressed:() async {
                final ok = await SosService.send(rideId:widget.rideId);
                if(context.mounted){
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content:Text(ok ? "Alerte SOS transmise." : "Impossible d'envoyer l'alerte.")),
                  );
                }
              },
              icon:const Icon(Icons.sos),
              label:const Text("SOS — ASSISTANCE"),
            ),
          ]),
        ),
    );
  }
}

class DriverPage extends StatefulWidget {
  final Map<String,dynamic> user;
  const DriverPage({super.key,required this.user});
  @override State<DriverPage> createState()=>_DriverPageState();
}
class _DriverPageState extends State<DriverPage>{
  bool available=false;
  List<dynamic> rides=[];
  bool loading=false;

  Future<String?> token() async => (await SharedPreferences.getInstance()).getString("token");

  Future<void> setStatus(bool value) async {
    final t=await token();
    final pos = value ? await LocationService.current() : null;
    await http.post(Uri.parse("$apiBaseUrl/drivers/status"),
      headers:{"Content-Type":"application/json","Authorization":"Bearer $t"},
      body:jsonEncode({
        "status":value?"available":"offline",
        "lat":pos?.latitude,
        "lng":pos?.longitude
      }));
    setState(()=>available=value);
  }

  Future<void> refresh() async {
    final t=await token();
    final r=await http.get(Uri.parse("$apiBaseUrl/rides"),
      headers:{"Authorization":"Bearer $t"});
    if(r.statusCode==200) setState(()=>rides=jsonDecode(r.body));
  }

  Future<void> action(int id,String action) async {
    final t=await token();
    final r=await http.post(Uri.parse("$apiBaseUrl/rides/$id/$action"),
      headers:{"Content-Type":"application/json","Authorization":"Bearer $t"},
      body:jsonEncode({"final_fare":5000}));
    if(r.statusCode<300) refresh();
  }

  @override void initState(){super.initState();refresh();}
  @override Widget build(BuildContext context)=>Scaffold(
    appBar:AppBar(title:const Text("Espace Chauffeur"),backgroundColor:const Color(0xFFF5C400)),
    body:RefreshIndicator(onRefresh:refresh,child:ListView(padding:const EdgeInsets.all(18),children:[
      Card(child:SwitchListTile(
        title:const Text("Je suis disponible",style:TextStyle(fontWeight:FontWeight.w700)),
        subtitle:Text(available?"Vous pouvez recevoir des courses":"Vous êtes hors ligne"),
        value:available,onChanged:setStatus)),
      const SizedBox(height:12),
      OutlinedButton.icon(
        onPressed:()=>Navigator.push(context,MaterialPageRoute(builder:(_)=>const WalletPage())),
        icon:const Icon(Icons.account_balance_wallet),
        label:const Text("MES REVENUS"),
      ),
      const SizedBox(height:12),
      const Text("Demandes de course",style:TextStyle(fontSize:22,fontWeight:FontWeight.w800)),
      const SizedBox(height:8),
      ...rides.map((r)=>Card(child:ListTile(
        leading:const Icon(Icons.local_taxi),
        title:Text("${r["pickup"]} → ${r["destination"]}"),
        subtitle:Text("Statut : ${r["status"]}\nEstimation : ${r["estimated_fare"]} FCFA"),
        isThreeLine:true,
        trailing: r["status"]=="requested"
          ? FilledButton(onPressed:()=>action(r["id"],"accept"),child:const Text("ACCEPTER"))
          : r["status"]=="accepted"
            ? FilledButton(onPressed:()=>action(r["id"],"start"),child:const Text("DÉMARRER"))
            : r["status"]=="in_progress"
              ? FilledButton(onPressed:()=>action(r["id"],"complete"),child:const Text("TERMINER"))
              : null,
      ))).toList()
    ])),
  );
}
