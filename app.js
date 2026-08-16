const API="http://127.0.0.1:5000/api";
let token=localStorage.getItem("taxi_token")||"";

function login(){
  const phone=document.getElementById("phone").value;
  const password=document.getElementById("password").value;
  fetch(API+"/auth/login",{method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify({phone,password})})
    .then(r=>r.json()).then(d=>{
      if(d.token && d.user.role==="admin"){
        token=d.token; localStorage.setItem("taxi_token",token);
        document.getElementById("login").style.display="none";
        loadAll();
      } else alert("Compte administrateur requis.");
    });
}

async function loadAll(){
  if(!token){document.getElementById("login").style.display="flex";return;}
  const r=await fetch(API+"/admin/dashboard",{headers:{Authorization:"Bearer "+token}});
  if(r.ok){
    render(await r.json());
    document.getElementById("login").style.display="none";
  } else document.getElementById("login").style.display="flex";
}

function render(d){
 const items=[
   ["Passagers",d.passengers],
   ["Chauffeurs",d.drivers],
   ["Taxis disponibles",d.available_drivers],
   ["Courses",d.rides],
   ["Demandes en attente",d.requested_rides]
 ];
 document.getElementById("cards").innerHTML=items.map(x=>
   `<div class="card"><span>${x[0]}</span><strong>${x[1]}</strong></div>`
 ).join("");
}
loadAll();

async function loadSos(){
  if(!token) return;
  const r=await fetch(API+"/admin/sos",{headers:{Authorization:"Bearer "+token}});
  if(!r.ok)return;
  const data=await r.json();
  document.getElementById("sos").innerHTML=data.length
    ? data.map(a=>`<div class="taxi"><b>SOS #${a.id}</b><span>${a.status}</span><span>${a.lat ?? "—"}, ${a.lng ?? "—"}</span></div>`).join("")
    : "Aucune alerte SOS.";
}
async function loadAll(){
  if(!token){document.getElementById("login").style.display="flex";return;}
  const r=await fetch(API+"/admin/dashboard",{headers:{Authorization:"Bearer "+token}});
  if(r.ok){
    render(await r.json());
    document.getElementById("login").style.display="none";
    loadSos();
  } else document.getElementById("login").style.display="flex";
}

async function loadFinance(){
  if(!token)return;
  const r=await fetch(API+"/admin/finance",{headers:{Authorization:"Bearer "+token}});
  if(!r.ok)return;
  const d=await r.json();
  document.getElementById("finance").innerHTML=[
    ["Paiements réglés",d.payments_paid],
    ["CA brut",d.gross_revenue+" FCFA"],
    ["Commissions",d.commission_revenue+" FCFA"],
    ["Net chauffeurs",d.driver_net+" FCFA"]
  ].map(x=>`<div class="card"><span>${x[0]}</span><strong>${x[1]}</strong></div>`).join("");
}
setInterval(loadFinance,15000);
setTimeout(loadFinance,1500);

async function createUser(){
  const body={
    name:document.getElementById("newName").value.trim(),
    phone:document.getElementById("newPhone").value.trim(),
    password:document.getElementById("newPassword").value,
    role:document.getElementById("newRole").value
  };
  const r=await fetch(API+"/admin/users",{
    method:"POST",
    headers:{"Content-Type":"application/json","Authorization":"Bearer "+token},
    body:JSON.stringify(body)
  });
  const d=await r.json();
  if(r.ok){ alert("Compte créé."); loadUsers(); }
  else alert(d.error||"Création impossible.");
}
async function loadUsers(){
  if(!token)return;
  const r=await fetch(API+"/admin/users",{headers:{Authorization:"Bearer "+token}});
  if(!r.ok)return;
  const data=await r.json();
  document.getElementById("users").innerHTML=data.map(u=>
    `<div class="taxi"><span>#${u.id}</span><b>${u.name}</b><span>${u.phone}<br>${u.role} · ${u.active?"actif":"désactivé"}</span></div>`
  ).join("");
}
setTimeout(loadUsers,1200);
