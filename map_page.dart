import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

class TaxiMapPage extends StatelessWidget {
  final double latitude;
  final double longitude;
  final String title;

  const TaxiMapPage({
    super.key,
    required this.latitude,
    required this.longitude,
    this.title = "Carte TAXI SENIRAN AIBD",
  });

  @override
  Widget build(BuildContext context) {
    final center = LatLng(latitude, longitude);
    return Scaffold(
      appBar: AppBar(
        title: Text(title),
        backgroundColor: const Color(0xFFF5C400),
      ),
      body: FlutterMap(
        options: MapOptions(
          initialCenter: center,
          initialZoom: 14.5,
        ),
        children: [
          TileLayer(
            urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
            userAgentPackageName: 'sn.aibd.taxi_seniran',
          ),
          MarkerLayer(
            markers: [
              Marker(
                point: center,
                width: 54,
                height: 54,
                child: const Icon(
                  Icons.location_pin,
                  size: 48,
                  color: Color(0xFF143B70),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
