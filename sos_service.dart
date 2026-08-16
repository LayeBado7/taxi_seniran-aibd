import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'config.dart';

class SosService {
  static Future<bool> send({int? rideId, double? lat, double? lng}) async {
    final p = await SharedPreferences.getInstance();
    final token = p.getString("token");
    if (token == null) return false;
    final r = await http.post(
      Uri.parse("$apiBaseUrl/sos"),
      headers: {"Content-Type": "application/json", "Authorization": "Bearer $token"},
      body: jsonEncode({"ride_id": rideId, "lat": lat, "lng": lng}),
    );
    return r.statusCode == 201;
  }
}
