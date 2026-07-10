import 'package:flutter/material.dart';

import '../api_client.dart';
import '../data/rwanda_locations.dart';
import '../models/pregnancy.dart';
import '../utils/dates.dart';
import 'dashboard_screen.dart';

/// Create or edit the pregnancy profile. Pass [existing] for edit mode.
class PregnancyFormScreen extends StatefulWidget {
  final Pregnancy? existing;

  const PregnancyFormScreen({super.key, this.existing});

  @override
  State<PregnancyFormScreen> createState() => _PregnancyFormScreenState();
}

class _PregnancyFormScreenState extends State<PregnancyFormScreen> {
  final _fullNameController = TextEditingController();
  final _ageController = TextEditingController();
  final _healthPostController = TextEditingController();

  String? _province;
  String? _district;
  String? _hospital;
  int _gravida = 1;
  int _parity = 0;
  DateTime? _lmpDate;
  bool _isLmpEstimated = false;
  bool _isSaving = false;

  bool get _isEditMode => widget.existing != null;

  @override
  void initState() {
    super.initState();
    final existing = widget.existing;
    if (existing != null) {
      _fullNameController.text = existing.fullName;
      _ageController.text = existing.age.toString();
      _healthPostController.text = existing.healthPost;
      _province = existing.province.isEmpty ? null : existing.province;
      _district = existing.district.isEmpty ? null : existing.district;
      _hospital = existing.hospital.isEmpty ? null : existing.hospital;
      _gravida = existing.gravida;
      _parity = existing.parity;
      _lmpDate = existing.lmpDate;
      _isLmpEstimated = existing.isLmpEstimated;
    }
  }

  @override
  void dispose() {
    _fullNameController.dispose();
    _ageController.dispose();
    _healthPostController.dispose();
    super.dispose();
  }

  List<String> get _districtOptions =>
      _province == null ? [] : (rwandaDistrictsByProvince[_province] ?? []);

  List<String> get _hospitalOptions {
    if (_district == null) return [];
    final options =
        List<String>.from(rwandaHospitalsByDistrict[_district] ?? []);
    // A stored value not in the hardcoded list (e.g. data entered before a
    // list update) must still appear, or the dropdown would crash.
    if (_hospital != null && !options.contains(_hospital)) {
      options.add(_hospital!);
    }
    return options;
  }

  // ---- LMP selection ----

  Future<void> _pickExactLmp() async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: _lmpDate ?? now,
      firstDate: now.subtract(const Duration(days: 42 * 7)),
      lastDate: now,
    );
    if (picked != null) {
      setState(() {
        _lmpDate = picked;
        _isLmpEstimated = false;
      });
    }
  }

  Future<void> _pickEstimatedLmp() async {
    final months = await showModalBottomSheet<int>(
      context: context,
      builder: (context) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Umaze igihe kingana iki utwite?',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 16),
              Wrap(
                spacing: 12,
                runSpacing: 12,
                children: [
                  for (final n in [1, 2, 3, 4, 5])
                    ActionChip(
                      label: Text(
                        n == 1 ? 'Ukwezi 1' : 'Amezi $n',
                        style: const TextStyle(fontSize: 18),
                      ),
                      padding: const EdgeInsets.all(12),
                      onPressed: () => Navigator.of(context).pop(n),
                    ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
    if (months != null) {
      setState(() {
        _lmpDate = monthsAgo(months);
        _isLmpEstimated = true;
      });
    }
  }

  // ---- Validation & submit ----

  String? _validate() {
    if (_province == null || _district == null || _hospital == null) {
      return 'Hitamo intara, akarere n\'ivuriro.';
    }
    if (_fullNameController.text.trim().isEmpty) {
      return 'Andika amazina yawe yose.';
    }
    final age = int.tryParse(_ageController.text.trim());
    if (age == null || age < 12 || age > 60) {
      return 'Imyaka igomba kuba hagati ya 12 na 60.';
    }
    if (_gravida < 1) {
      return 'Inda igomba kuba nibura iya 1.';
    }
    if (_parity >= _gravida) {
      return 'Imbyaro zigomba kuba munsi y\'inda utwite.';
    }
    final lmp = _lmpDate;
    if (lmp == null) {
      return 'Hitamo itariki waherukiye mu mihango.';
    }
    final daysAgo = DateTime.now().difference(lmp).inDays;
    if (daysAgo < 0) {
      return 'Itariki y\'imihango ntishobora kuba mu bihe bizaza.';
    }
    if (daysAgo > 42 * 7) {
      return 'Itariki y\'imihango ntishobora kurenga ibyumweru 42.';
    }
    return null;
  }

  Future<void> _submit() async {
    final error = _validate();
    if (error != null) {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text(error)));
      return;
    }

    setState(() => _isSaving = true);
    final body = {
      'full_name': _fullNameController.text.trim(),
      'age': int.parse(_ageController.text.trim()),
      'gravida': _gravida,
      'parity': _parity,
      'lmp_date': _lmpDate!.toIso8601String().substring(0, 10),
      'is_lmp_estimated': _isLmpEstimated,
      'province': _province,
      'district': _district,
      'hospital': _hospital,
      'health_centre': '',
      'health_post': _healthPostController.text.trim(),
    };
    try {
      final pregnancy = _isEditMode
          ? await ApiClient.updatePregnancy(body)
          : await ApiClient.createPregnancy(body);
      if (!mounted) return;
      Navigator.of(context).pushAndRemoveUntil(
        MaterialPageRoute(builder: (_) => DashboardScreen(pregnancy: pregnancy)),
        (route) => false,
      );
    } on ApiException catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text(e.message)));
    } finally {
      if (mounted) setState(() => _isSaving = false);
    }
  }

  // ---- Widgets ----

  Widget _sectionTitle(String text) => Padding(
        padding: const EdgeInsets.only(top: 24, bottom: 12),
        child: Text(
          text,
          style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
      );

  Widget _dropdown({
    required String label,
    required String? value,
    required List<String> options,
    required ValueChanged<String?> onChanged,
    bool enabled = true,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: DropdownButtonFormField<String>(
        initialValue: value,
        items: [
          for (final option in options)
            DropdownMenuItem(value: option, child: Text(option)),
        ],
        onChanged: enabled ? onChanged : null,
        isExpanded: true,
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
      ),
    );
  }

  Widget _stepper({
    required String label,
    required int value,
    required int min,
    required ValueChanged<int> onChanged,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        children: [
          Expanded(child: Text(label, style: const TextStyle(fontSize: 18))),
          IconButton.outlined(
            onPressed: value > min ? () => onChanged(value - 1) : null,
            icon: const Icon(Icons.remove),
          ),
          SizedBox(
            width: 48,
            child: Text(
              '$value',
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            ),
          ),
          IconButton.outlined(
            onPressed: () => onChanged(value + 1),
            icon: const Icon(Icons.add),
          ),
        ],
      ),
    );
  }

  Widget _lmpCard({
    required String emoji,
    required String label,
    required bool selected,
    required VoidCallback onTap,
  }) {
    return Expanded(
      child: Card(
        color: selected
            ? Theme.of(context).colorScheme.primaryContainer
            : null,
        child: InkWell(
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 8),
            child: Column(
              children: [
                Text(emoji, style: const TextStyle(fontSize: 32)),
                const SizedBox(height: 8),
                Text(
                  label,
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 16),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final lmp = _lmpDate;
    return Scaffold(
      appBar: AppBar(
        title: Text(_isEditMode ? 'Hindura amakuru yawe' : 'Amakuru y\'inda'),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(24),
          children: [
            _sectionTitle('Ivuriro ry\'ubuzima'),
            _dropdown(
              label: 'Intara',
              value: _province,
              options: rwandaProvinces,
              onChanged: (value) => setState(() {
                _province = value;
                _district = null;
                _hospital = null;
              }),
            ),
            _dropdown(
              label: 'Akarere',
              value: _district,
              options: _districtOptions,
              enabled: _province != null,
              onChanged: (value) => setState(() {
                _district = value;
                _hospital = null;
              }),
            ),
            _dropdown(
              label: 'Ibitaro / Ikigo nderabuzima',
              value: _hospital,
              options: _hospitalOptions,
              enabled: _district != null,
              onChanged: (value) => setState(() => _hospital = value),
            ),
            TextField(
              controller: _healthPostController,
              style: const TextStyle(fontSize: 18),
              decoration: const InputDecoration(
                labelText: 'Ivuriro ry\'ibanze',
                hintText: 'Andika izina ry\'ivuriro',
                border: OutlineInputBorder(),
              ),
            ),
            _sectionTitle('Amakuru yawe'),
            TextField(
              controller: _fullNameController,
              style: const TextStyle(fontSize: 18),
              decoration: const InputDecoration(
                labelText: 'Amazina yawe yose',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _ageController,
              keyboardType: TextInputType.number,
              style: const TextStyle(fontSize: 18),
              decoration: const InputDecoration(
                labelText: 'Imyaka yawe',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            _stepper(
              label: 'Inda ya',
              value: _gravida,
              min: 1,
              onChanged: (value) => setState(() => _gravida = value),
            ),
            _stepper(
              label: 'Imbyaro ya',
              value: _parity,
              min: 0,
              onChanged: (value) => setState(() => _parity = value),
            ),
            const Text(
              'Itariki uherukira mumihango',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                _lmpCard(
                  emoji: '📅',
                  label: 'Nzi itariki nyayo',
                  selected: lmp != null && !_isLmpEstimated,
                  onTap: _pickExactLmp,
                ),
                const SizedBox(width: 12),
                _lmpCard(
                  emoji: '❓',
                  label: 'Simbizi neza',
                  selected: lmp != null && _isLmpEstimated,
                  onTap: _pickEstimatedLmp,
                ),
              ],
            ),
            if (lmp != null) ...[
              const SizedBox(height: 8),
              Text(
                'LMP: ${formatDdMmYyyy(lmp)}'
                '${_isLmpEstimated ? ' (uko bigereranijwe)' : ''}',
                style: const TextStyle(fontSize: 16),
              ),
              const SizedBox(height: 12),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Itariki azabyara (uko bigereranijwe): '
                        '${formatDdMmYyyy(calculateEdd(lmp))}',
                        style: const TextStyle(fontSize: 18),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Utwite ibyumweru ${weeksSince(lmp)}',
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: _isSaving ? null : _submit,
              child: _isSaving
                  ? const SizedBox(
                      height: 24,
                      width: 24,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text('Bika'),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }
}
