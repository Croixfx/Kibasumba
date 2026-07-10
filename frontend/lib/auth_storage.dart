import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Wraps flutter_secure_storage for the auth token and phone number so
/// no other file talks to secure storage directly.
class AuthStorage {
  static const _storage = FlutterSecureStorage();
  static const _tokenKey = 'auth_token';
  static const _phoneKey = 'phone_number';

  static Future<void> saveSession(String token, String phoneNumber) async {
    await _storage.write(key: _tokenKey, value: token);
    await _storage.write(key: _phoneKey, value: phoneNumber);
  }

  static Future<String?> readToken() => _storage.read(key: _tokenKey);

  static Future<void> clearSession() async {
    await _storage.delete(key: _tokenKey);
    await _storage.delete(key: _phoneKey);
  }
}
