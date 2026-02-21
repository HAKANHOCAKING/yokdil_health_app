import 'package:dio/dio.dart';
import '../../../core/network/api_client.dart';
import '../domain/vocab_models.dart';

class VocabRepository {
  final ApiClient _apiClient;

  VocabRepository(this._apiClient);

  Dio get _dio => _apiClient.dio;

  // --- Vocab Sets ---

  Future<List<VocabSet>> getSets() async {
    final res = await _dio.get('/vocab/sets');
    return (res.data['sets'] as List)
        .map((s) => VocabSet.fromJson(s))
        .toList();
  }

  Future<List<VocabWord>> getSetWords(String setId,
      {int page = 1, int perPage = 50}) async {
    final res = await _dio.get('/vocab/sets/$setId/words',
        queryParameters: {'page': page, 'per_page': perPage});
    return (res.data['words'] as List)
        .map((w) => VocabWord.fromJson(w))
        .toList();
  }

  // --- Review Queue ---

  Future<List<VocabWord>> getReviewQueue({int limit = 20, String? setId}) async {
    final params = <String, dynamic>{'limit': limit};
    if (setId != null) params['set_id'] = setId;
    final res = await _dio.get('/progress/review-queue', queryParameters: params);
    return (res.data['words'] as List)
        .map((w) => VocabWord.fromJson(w))
        .toList();
  }

  Future<List<VocabWord>> getNewWords(String setId, {int limit = 10}) async {
    final res = await _dio.get('/progress/new-words',
        queryParameters: {'set_id': setId, 'limit': limit});
    return (res.data['words'] as List)
        .map((w) => VocabWord.fromJson(w))
        .toList();
  }

  // --- Study Session ---

  Future<String> startSession(String mode) async {
    final res = await _dio.post('/progress/sessions/start', data: {'mode': mode});
    return res.data['session_id'];
  }

  Future<Map<String, dynamic>> endSession(String sessionId) async {
    final res = await _dio.post('/progress/sessions/$sessionId/end');
    return res.data;
  }

  // --- Review ---

  Future<Map<String, dynamic>> reviewWord({
    required String wordId,
    required int quality,
    String? sessionId,
    int timeSpentMs = 0,
  }) async {
    final res = await _dio.post('/progress/review', data: {
      'word_id': wordId,
      'quality': quality,
      'session_id': sessionId,
      'time_spent_ms': timeSpentMs,
    });
    return res.data;
  }

  // --- Stats ---

  Future<StudyStats> getStats() async {
    final res = await _dio.get('/progress/stats');
    return StudyStats.fromJson(res.data);
  }

  // --- Quiz ---

  Future<List<QuizQuestion>> generateQuiz({
    required String setId,
    String mode = 'en_tr',
    int count = 10,
  }) async {
    final res = await _dio.get('/vocab/quiz', queryParameters: {
      'set_id': setId,
      'mode': mode,
      'count': count,
    });
    return (res.data['questions'] as List)
        .map((q) => QuizQuestion.fromJson(q))
        .toList();
  }
}
