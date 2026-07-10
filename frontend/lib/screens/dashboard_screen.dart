import 'dart:io';

import 'package:flutter/material.dart';
import 'package:open_file/open_file.dart';
import 'package:path_provider/path_provider.dart';

import '../api_client.dart';
import '../auth_storage.dart';
import '../models/pregnancy.dart';
import '../utils/dates.dart';
import 'phone_entry_screen.dart';

/// Sprint 5: minimal woman-facing home screen. Her data is maintained by
/// the midwife in the admin panel; here she sees her status and downloads
/// the official Ifishi PDF.
class DashboardScreen extends StatefulWidget {
  final Pregnancy pregnancy;

  const DashboardScreen({super.key, required this.pregnancy});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  bool _isDownloading = false;

  Future<void> _logout() async {
    await AuthStorage.clearSession();
    if (!mounted) return;
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const PhoneEntryScreen()),
      (route) => false,
    );
  }

  Future<void> _downloadCard() async {
    setState(() => _isDownloading = true);
    try {
      final bytes = await ApiClient.downloadCard();
      final dir = await getApplicationDocumentsDirectory();
      final path =
          '${dir.path}/ifishi_${DateTime.now().millisecondsSinceEpoch}.pdf';
      await File(path).writeAsBytes(bytes);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Ifishi yawe yagurujwe neza ✓')),
        );
      }
      await OpenFile.open(path);
    } on ApiException catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text(e.message)));
    } finally {
      if (mounted) setState(() => _isDownloading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final pregnancy = widget.pregnancy;
    // Live-calculated so the shown week is current even if the record is
    // a few weeks old.
    final weeks = weeksSince(pregnancy.lmpDate);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Murakaza neza'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Gusohoka',
            onPressed: _logout,
          ),
        ],
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(24),
          children: [
            Text(
              pregnancy.fullName,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 26, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              'Utwite ibyumweru $weeks',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 18,
                color: Theme.of(context).colorScheme.primary,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 32),
            Card(
              elevation: 2,
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  children: [
                    Icon(
                      Icons.description,
                      size: 72,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      "Ifishi y'Ubuzima bw'Umubyeyi n'Umwana",
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Tapfa hano kuyikurura',
                      textAlign: TextAlign.center,
                      style: TextStyle(fontSize: 14, color: Colors.grey),
                    ),
                    const SizedBox(height: 20),
                    ElevatedButton(
                      onPressed: _isDownloading ? null : _downloadCard,
                      child: _isDownloading
                          ? const SizedBox(
                              height: 24,
                              width: 24,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Text('📥 Pakurura Ifishi yanjye'),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            Card(
              color: Colors.grey.shade200,
              elevation: 0,
              child: const Padding(
                padding: EdgeInsets.all(20),
                child: Column(
                  children: [
                    Icon(Icons.school, color: Colors.grey, size: 32),
                    SizedBox(height: 8),
                    Text(
                      "Inyigisho z'ubuzima — Ejo hazaza",
                      textAlign: TextAlign.center,
                      style: TextStyle(color: Colors.grey, fontSize: 15),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
