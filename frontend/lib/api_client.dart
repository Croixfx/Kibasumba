import 'dart:convert';

import 'package:http/http.dart' as http;

import 'auth_storage.dart';
import 'models/pregnancy.dart';

/// Backend base URL. 10.0.2.2 is how the Android emulator reaches the host
/// machine's 127.0.0.1. Change this for a real device or production server.
const String baseUrl = 'http://10.0.2.2:8000';

class ApiException implements Exception {
  final String message;
  final int? statusCode;

  ApiException(this.message, {this.statusCode});

  @override
  String toString() => message;
}

/// Centralizes all HTTP calls to the backend so screens never call
/// `http.post` directly.
class ApiClient {
  static Uri _authUri(String path) => Uri.parse('$baseUrl/api/auth/$path');
  static Uri _pregnancyUri(String path) =>
      Uri.parse('$baseUrl/api/pregnancy/$path');

  static Future<Map<String, dynamic>> _request(
    String method,
    Uri uri, {
    Map<String, dynamic>? body,
    bool authenticated = false,
  }) async {
    final headers = {'Content-Type': 'application/json'};
    if (authenticated) {
      final token = await AuthStorage.readToken();
      headers['Authorization'] = 'Token $token';
    }

    http.Response response;
    try {
      final request = http.Request(method, uri)..headers.addAll(headers);
      if (body != null) {
        request.body = jsonEncode(body);
      }
      response = await http.Response.fromStream(await request.send());
    } catch (_) {
      throw ApiException(
        "Ntibyashobotse kugera kuri seriveri. Reba interineti yawe.",
      );
    }

    Map<String, dynamic> decoded = {};
    if (response.body.isNotEmpty) {
      try {
        final parsed = jsonDecode(response.body);
        if (parsed is Map<String, dynamic>) {
          decoded = parsed;
        }
      } catch (_) {
        // Malformed/non-JSON body; fall through to status-based error below.
      }
    }

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return decoded;
    }

    throw ApiException(
      _extractErrorMessage(decoded),
      statusCode: response.statusCode,
    );
  }

  static Future<Map<String, dynamic>> _post(
    String path,
    Map<String, dynamic> body,
  ) => _request('POST', _authUri(path), body: body);

  // The backend reports errors either as {"error": "..."} (view-level
  // checks) or as DRF serializer errors like {"phone_number": ["msg"]}.
  static String _extractErrorMessage(Map<String, dynamic> body) {
    if (body.isEmpty) return 'Habayeho ikibazo. Ongera ugerageze.';
    final error = body['error'];
    if (error is String) return error;

    final messages = <String>[];
    for (final value in body.values) {
      if (value is List) {
        messages.addAll(value.map((e) => e.toString()));
      } else if (value is String) {
        messages.add(value);
      }
    }
    return messages.isNotEmpty
        ? messages.join('\n')
        : 'Habayeho ikibazo. Ongera ugerageze.';
  }

  // ---- Auth (Sprint 1/2) ----

  static Future<void> requestOtp(String phoneNumber) =>
      _post('request-otp/', {'phone_number': phoneNumber});

  static Future<void> verifyOtp(String phoneNumber, String code) =>
      _post('verify-otp/', {'phone_number': phoneNumber, 'code': code});

  static Future<Map<String, dynamic>> setPassword(
    String phoneNumber,
    String password,
  ) => _post('set-password/', {
    'phone_number': phoneNumber,
    'password': password,
  });

  static Future<Map<String, dynamic>> login(
    String phoneNumber,
    String password,
  ) => _post('login/', {'phone_number': phoneNumber, 'password': password});

  /// Who is logged in and what role they have (Sprint 3.5).
  static Future<Map<String, dynamic>> getMe() =>
      _request('GET', _authUri('me/'), authenticated: true);

  /// Downloads the woman's Ifishi PDF as raw bytes (Sprint 5).
  static Future<List<int>> downloadCard() async {
    final token = await AuthStorage.readToken();
    http.Response response;
    try {
      response = await http.get(
        _pregnancyUri('download-card/'),
        headers: {'Authorization': 'Token $token'},
      );
    } catch (_) {
      throw ApiException(
        "Ntibyashobotse kugera kuri seriveri. Reba interineti yawe.",
      );
    }
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return response.bodyBytes;
    }
    Map<String, dynamic> decoded = {};
    try {
      final parsed = jsonDecode(response.body);
      if (parsed is Map<String, dynamic>) decoded = parsed;
    } catch (_) {
      // Non-JSON error body; fall through to the generic message.
    }
    throw ApiException(
      _extractErrorMessage(decoded),
      statusCode: response.statusCode,
    );
  }

  // ---- Pregnancy (Sprint 3) ----

  /// Returns the active pregnancy, or null if the mother has none (404).
  static Future<Pregnancy?> getActivePregnancy() async {
    try {
      final data = await _request(
        'GET',
        _pregnancyUri('active/'),
        authenticated: true,
      );
      return Pregnancy.fromJson(data);
    } on ApiException catch (e) {
      if (e.statusCode == 404) return null;
      rethrow;
    }
  }

  static Future<Pregnancy> createPregnancy(Map<String, dynamic> body) async {
    final data = await _request(
      'POST',
      _pregnancyUri('create/'),
      body: body,
      authenticated: true,
    );
    return Pregnancy.fromJson(data);
  }

  static Future<Pregnancy> updatePregnancy(Map<String, dynamic> body) async {
    final data = await _request(
      'PATCH',
      _pregnancyUri('update/'),
      body: body,
      authenticated: true,
    );
    return Pregnancy.fromJson(data);
  }
}
