import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../../data/vocab_repository.dart';
import '../../domain/vocab_models.dart';

final vocabRepositoryProvider = Provider<VocabRepository>((ref) {
  return VocabRepository(ref.watch(apiClientProvider));
});

// --- Vocab Sets ---

final vocabSetsProvider = FutureProvider<List<VocabSet>>((ref) async {
  return ref.watch(vocabRepositoryProvider).getSets();
});

// --- Stats ---

final studyStatsProvider = FutureProvider<StudyStats>((ref) async {
  return ref.watch(vocabRepositoryProvider).getStats();
});

// --- Review Queue ---

final reviewQueueProvider = FutureProvider<List<VocabWord>>((ref) async {
  return ref.watch(vocabRepositoryProvider).getReviewQueue();
});
