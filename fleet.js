const API_FLEET="http://127.0.0.1:5000/api";
async function loadFleet(){
  const token=localStorage.getItem("taxi_token");
  if(!token)return;
  const r=await fetch(API_FLEET+"/admin/fleet",{headers:{Authorization:"Bearer "+token}});
  if(!r.ok)return;
  const data=await r.json();
  const el=document.getElementById("fleet");
  el.innerHTML=data.map(d=>`
    <div class="taxi">
      <span>#${d.queue_position ?? "—"}</span>
      <b>${d.name}<br>${d.vehicle.plate ?? "Sans véhicule"}</b>
      <span>${d.status}<br>${d.rating.toFixed(1)} ⭐</span>
    </div>`).join("");
}
setInterval(loadFleet,10000);
setTimeout(loadFleet,1000);
