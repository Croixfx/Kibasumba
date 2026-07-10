import 'package:flutter/material.dart';

import '../api_client.dart';
import '../auth_storage.dart';
import 'dashboard_screen.dart';
import 'phone_entry_screen.dart';
import 'pregnancy_form_screen.dart';
import 'staff_placeholder_screen.dart';

/// Entry point after authentication (both app start and fresh logins).
/// Checks the role first: staff accounts go straight to the placeholder
/// screen. Women continue to the dashboard (active pregnancy) or the
/// create form (none). An invalid token restarts the auth flow.
class PregnancyGate extends StatefulWidget {
  const PregnancyGate({super.key});

  @override
  State<PregnancyGate> createState() => _PregnancyGateState();
}

class _PregnancyGateState extends State<PregnancyGate> {
  late Future<Widget> _future;

  @override
  void initState() {
    super.initState();
    _future = _resolve();
  }

  Future<Widget> _resolve() async {
    try {
      final me = await ApiClient.getMe();
      if (me['role'] != 'woman') {
        return const StaffPlaceholderScreen();
      }
      final pregnancy = await ApiClient.getActivePregnancy();
      return pregnancy == null
          ? const PregnancyFormScreen()
          : DashboardScreen(pregnancy: pregnancy);
    } on ApiException catch (e) {
      if (e.statusCode == 401) {
        // Stale or revoked token: restart the auth flow.
        await AuthStorage.clearSession();
        return const PhoneEntryScreen();
      }
      rethrow;
    }
  }

  void _retry() {
    setState(() => _future = _resolve());
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<Widget>(
      future: _future,
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }
        if (snapshot.hasError) {
          return Scaffold(
            body: SafeArea(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      snapshot.error.toString(),
                      textAlign: TextAlign.center,
                      style: const TextStyle(fontSize: 16),
                    ),
                    const SizedBox(height: 24),
                    ElevatedButton(
                      onPressed: _retry,
                      child: const Text('Ongera ugerageze'),
                    ),
                  ],
                ),
              ),
            ),
          );
        }
        return snapshot.data!;
      },
    );
  }
}
