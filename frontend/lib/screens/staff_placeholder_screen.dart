import 'package:flutter/material.dart';

import '../auth_storage.dart';
import 'phone_entry_screen.dart';

/// Shown when a staff account (midwife/chw/admin) logs into the mobile app.
/// Their dashboard lives in the React admin, not in Flutter — this screen
/// just tells them they're in the wrong place.
class StaffPlaceholderScreen extends StatelessWidget {
  const StaffPlaceholderScreen({super.key});

  Future<void> _logout(BuildContext context) async {
    await AuthStorage.clearSession();
    if (!context.mounted) return;
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const PhoneEntryScreen()),
      (route) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text(
                'Injira kuri dashboard ya mubuzi',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),
              ElevatedButton(
                onPressed: () => _logout(context),
                child: const Text('Gusohoka'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
