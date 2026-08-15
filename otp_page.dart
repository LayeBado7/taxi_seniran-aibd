import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'config.dart';

class OtpPage extends StatefulWidget {
  final String phone;
  const OtpPage({super.key, required this.phone});
  @override State<OtpPage> createState() => _OtpPageState();
}

class _OtpPageState extends State<OtpPage> {
  final code = TextEditingController();
  bool loading = false;

  Future<void> verify() async {
    setState(() => loading = true);
    final r = await http.post(
      Uri.parse("$apiBaseUrl/auth/verify-otp"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"phone": widget.phone, "code": code.text.trim()}),
    );
    setState(() => loading = false);
    if (!mounted) return;
    if (r.statusCode == 200) {
      final d = jsonDecode(r.body);
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString("token", d["token"]);
      Navigator.pop(context, d);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Code OTP invalide ou expiré.")),
      );
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      title: const Text("Vérification"),
      backgroundColor: const Color(0xFFF5C400),
    ),
    body: Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.sms, size: 70, color: Color(0xFF143B70)),
          const SizedBox(height: 15),
          Text("Code envoyé au ${widget.phone}", textAlign: TextAlign.center),
          TextField(
            controller: code,
            keyboardType: TextInputType.number,
            maxLength: 6,
            decoration: const InputDecoration(labelText: "Code OTP"),
          ),
          const SizedBox(height: 15),
          FilledButton(
            onPressed: loading ? null : verify,
            child: Text(loading ? "Vérification…" : "VALIDER"),
          ),
        ],
      ),
    ),
  );
}
