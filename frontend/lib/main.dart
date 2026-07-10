import 'package:flutter/material.dart';

import 'auth_storage.dart';
import 'screens/phone_entry_screen.dart';
import 'screens/pregnancy_gate.dart';

void main() {
  runApp(const KibasumbaApp());
}

class KibasumbaApp extends StatelessWidget {
  const KibasumbaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'kibasumba',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.teal),
        textTheme: const TextTheme(bodyMedium: TextStyle(fontSize: 16)),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            minimumSize: const Size.fromHeight(48),
            textStyle: const TextStyle(fontSize: 18),
          ),
        ),
      ),
      home: const StartupScreen(),
    );
  }
}

/// Checks for an existing token before deciding whether to enter the app
/// (via PregnancyGate, which checks the role and routes to the dashboard,
/// pregnancy form, or staff placeholder) or the start of the auth flow.
class StartupScreen extends StatelessWidget {
  const StartupScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<String?>(
      future: AuthStorage.readToken(),
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }
        final hasToken = snapshot.data != null;
        return hasToken ? const PregnancyGate() : const PhoneEntryScreen();
      },
    );
  }
}
