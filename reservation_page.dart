import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'config.dart';

class ReservationPage extends StatefulWidget {
  const ReservationPage({super.key});
  @override State<ReservationPage> createState()=>_ReservationPageState();
}
class _ReservationPageState extends State<ReservationPage>{
  final pickup=TextEditingController(text:"AIBD");
  final destination=TextEditingController();
  DateTime scheduled=DateTime.now().add(const Duration(hours:2));
  bool loading=false;

  Future<void> save() async {
    setState(()=>loading=true);
    final p=await SharedPreferences.getInstance();
    final t=p.getString("token");
    final r=await http.post(Uri.parse("$apiBaseUrl/reservations"),
      headers:{"Content-Type":"application/json","Authorization":"Bearer $t"},
      body:jsonEncode({
        "pickup":pickup.text,"destination":destination.text,
        "scheduled_at":scheduled.toIso8601String(),"estimated_fare":5000
      }));
    setState(()=>loading=false);
    if(!mounted)return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content:Text(r.statusCode==201?"Réservation enregistrée.":"Erreur de réservation.")
    ));
    if(r.statusCode==201) Navigator.pop(context);
  }

  @override Widget build(BuildContext context)=>Scaffold(
    appBar:AppBar(title:const Text("Réserver un taxi"),backgroundColor:const Color(0xFFF5C400)),
    body:ListView(padding:const EdgeInsets.all(20),children:[
      TextField(controller:pickup,decoration:const InputDecoration(labelText:"Départ")),
      TextField(controller:destination,decoration:const InputDecoration(labelText:"Destination")),
      const SizedBox(height:15),
      ListTile(
        title:const Text("Date et heure"),
        subtitle:Text("${scheduled.day.toString().padLeft(2,'0')}/${scheduled.month.toString().padLeft(2,'0')}/${scheduled.year} ${scheduled.hour.toString().padLeft(2,'0')}:${scheduled.minute.toString().padLeft(2,'0')}"),
        trailing:const Icon(Icons.calendar_month),
        onTap:() async {
          final d=await showDatePicker(context:context,firstDate:DateTime.now(),lastDate:DateTime.now().add(const Duration(days:90)),initialDate:scheduled);
          if(d==null)return;
          final t=await showTimePicker(context:context,initialTime:TimeOfDay.fromDateTime(scheduled));
          if(t!=null)setState(()=>scheduled=DateTime(d.year,d.month,d.day,t.hour,t.minute));
        },
      ),
      const SizedBox(height:15),
      FilledButton(onPressed:loading?null:save,child:Text(loading?"Enregistrement…":"CONFIRMER LA RÉSERVATION"))
    ])
  );
}
