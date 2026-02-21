import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../features/auth/presentation/pages/login_page.dart';
import '../../features/auth/presentation/pages/register_page.dart';
import '../../features/home/presentation/pages/home_page.dart';
import '../../features/questions/presentation/pages/question_page.dart';
import '../../features/questions/presentation/pages/question_list_page.dart';
import '../../features/sessions/presentation/pages/session_page.dart';
import '../../features/analytics/presentation/pages/analytics_page.dart';

// Vocabulary & SRS pages
import '../../features/vocab/presentation/pages/vocab_sets_page.dart';
import '../../features/vocab/presentation/pages/study_mode_page.dart';
import '../../features/vocab/presentation/pages/flashcard_study_page.dart';
import '../../features/vocab/presentation/pages/quiz_page.dart';
import '../../features/vocab/presentation/pages/review_queue_page.dart';
import '../../features/vocab/presentation/pages/progress_dashboard_page.dart';
import '../../features/vocab/presentation/pages/admin_vocab_page.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/login',
    routes: [
      GoRoute(
        path: '/login',
        name: 'login',
        builder: (context, state) => const LoginPage(),
      ),
      GoRoute(
        path: '/register',
        name: 'register',
        builder: (context, state) => const RegisterPage(),
      ),
      GoRoute(
        path: '/home',
        name: 'home',
        builder: (context, state) => const HomePage(),
      ),
      GoRoute(
        path: '/questions',
        name: 'questions',
        builder: (context, state) => const QuestionListPage(),
      ),
      GoRoute(
        path: '/question/:id',
        name: 'question',
        builder: (context, state) {
          final questionId = state.pathParameters['id']!;
          return QuestionPage(questionId: questionId);
        },
      ),
      GoRoute(
        path: '/session/:mode',
        name: 'session',
        builder: (context, state) {
          final mode = state.pathParameters['mode']!;
          return SessionPage(mode: mode);
        },
      ),
      GoRoute(
        path: '/analytics',
        name: 'analytics',
        builder: (context, state) => const AnalyticsPage(),
      ),

      // --- Vocabulary & Learning Routes ---
      GoRoute(
        path: '/vocab/sets',
        name: 'vocabSets',
        builder: (context, state) => const VocabSetsPage(),
      ),
      GoRoute(
        path: '/vocab/study',
        name: 'studyMode',
        builder: (context, state) {
          final setId = state.uri.queryParameters['setId'] ?? '';
          final setName = state.uri.queryParameters['setName'] ?? '';
          return StudyModePage(setId: setId, setName: setName);
        },
      ),
      GoRoute(
        path: '/vocab/flashcard',
        name: 'flashcard',
        builder: (context, state) {
          final setId = state.uri.queryParameters['setId'] ?? '';
          final setName = state.uri.queryParameters['setName'] ?? '';
          return FlashcardStudyPage(setId: setId, setName: setName);
        },
      ),
      GoRoute(
        path: '/vocab/quiz',
        name: 'quiz',
        builder: (context, state) {
          final setId = state.uri.queryParameters['setId'] ?? '';
          final mode = state.uri.queryParameters['mode'] ?? 'en_tr';
          return QuizPage(setId: setId, mode: mode);
        },
      ),
      GoRoute(
        path: '/vocab/review',
        name: 'reviewQueue',
        builder: (context, state) => const ReviewQueuePage(),
      ),
      GoRoute(
        path: '/vocab/dashboard',
        name: 'progressDashboard',
        builder: (context, state) => const ProgressDashboardPage(),
      ),
      GoRoute(
        path: '/admin/vocab',
        name: 'adminVocab',
        builder: (context, state) => const AdminVocabPage(),
      ),
    ],
  );
});
