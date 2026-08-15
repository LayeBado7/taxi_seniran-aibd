import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'config.dart';

class WalletPage extends StatefulWidget {
  const WalletPage({super.key});
  @override State<WalletPage> createState()=>_WalletPageState();
}
class _WalletPageState extends State<WalletPage>{
  Map<String,dynamic>? data;
  Future<void> load() async {
    final p=await SharedPreferences.getInstance();
    final t=p.getString("token");
    final r=await http.get(Uri.parse("$apiBaseUrl/drivers/wallet"),
      headers:{"Authorization":"Bearer $t"});
    if(r.statusCode==200) setState(()=>data=jsonDecode(r.body));
  }
  @override void initState(){super.initState();load();}
  @override Widget build(BuildContext context)=>Scaffold(
    appBar:AppBar(title:const Text("Mes revenus"),backgroundColor:const Color(0xFFF5C400)),
    body:data==null ? const Center(child:CircularProgressIndicator()) :
      ListView(padding:const EdgeInsets.all(20),children:[
        Card(child:ListTile(
          title:const Text("Solde disponible"),
          subtitle:Text("${data!["balance"]} FCFA",style:const TextStyle(fontSize:28,fontWeight:FontWeight.w800)),
        )),
        Card(child:ListTile(
          title:const Text("Revenus cumulés"),
          subtitle:Text("${data!["total_earned"]} FCFA"),
        )),
        Card(child:ListTile(
          title:const Text("Commissions"),
          subtitle:Text("${data!["total_commission"]} FCFA"),
        )),
      ])
  );
}
