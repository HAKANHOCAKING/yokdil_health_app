import 'package:dio/dio.dart';
import '../../../../core/network/api_client.dart';
import '../../domain/entities/user.dart';
import '../models/user_model.dart';

class AuthRepository {
  final ApiClient _apiClient;

  AuthRepository(this._apiClient);

  Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await _apiClient.dio.post(
        '/auth/login',
        data: {
          'email': email,
          'password': password,
        },
      );

      return response.data;
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<User> register({
    required String email,
    required String password,
    required String fullName,
    String role = 'student',
  }) async {
    try {
      final response = await _apiClient.dio.post(
        '/auth/register',
        data: {
          'email': email,
          'password': password,
          'full_name': fullName,
          'role': role,
        },
      );

      final userModel = UserModel.fromJson(response.data);
      return userModel.toEntity();
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<User> getCurrentUser() async {
    try {
      final response = await _apiClient.dio.get('/auth/me');
      final userModel = UserModel.fromJson(response.data);
      return userModel.toEntity();
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<void> logout() async {
    try {
      await _apiClient.dio.post('/auth/logout');
      await _apiClient.clearTokens();
    } catch (e) {
      // Still clear local tokens even if API call fails
      await _apiClient.clearTokens();
      throw _handleError(e);
    }
  }

  String _handleError(dynamic error) {
    if (error is DioException) {
      if (error.response != null) {
        final data = error.response!.data;
        if (data is Map && data.containsKey('detail')) {
          return data['detail'].toString();
        }
      }
      return error.message ?? 'Network error occurred';
    }
    return error.toString();
  }
}
