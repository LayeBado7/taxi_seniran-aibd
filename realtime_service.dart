import 'package:socket_io_client/socket_io_client.dart' as io;

class RealtimeService {
  late io.Socket socket;

  void connect(String baseUrl) {
    socket = io.io(
      baseUrl.replaceFirst('/api', ''),
      io.OptionBuilder().setTransports(['websocket']).disableAutoConnect().build(),
    );
    socket.connect();
  }

  void onDriverLocation(void Function(dynamic) handler) {
    socket.on('driver_location', handler);
  }

  void onSos(void Function(dynamic) handler) {
    socket.on('sos_alert', handler);
  }

  void dispose() {
    socket.dispose();
  }
}
