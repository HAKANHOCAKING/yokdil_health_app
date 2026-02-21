/// Vocabulary domain models

class VocabSet {
  final String id;
  final String name;
  final int wordCount;
  final String status;
  final String createdAt;

  VocabSet({
    required this.id,
    required this.name,
    required this.wordCount,
    required this.status,
    required this.createdAt,
  });

  factory VocabSet.fromJson(Map<String, dynamic> json) => VocabSet(
        id: json['id'] ?? '',
        name: json['name'] ?? '',
        wordCount: json['word_count'] ?? 0,
        status: json['status'] ?? 'draft',
        createdAt: json['created_at'] ?? '',
      );
}

class VocabWord {
  final String id;
  final String english;
  final String turkish;
  final String? exampleSentence;
  final String masteryLevel;
  final double? confidence;

  VocabWord({
    required this.id,
    required this.english,
    required this.turkish,
    this.exampleSentence,
    this.masteryLevel = 'new',
    this.confidence,
  });

  factory VocabWord.fromJson(Map<String, dynamic> json) => VocabWord(
        id: json['word_id'] ?? json['id'] ?? '',
        english: json['english'] ?? '',
        turkish: json['turkish'] ?? '',
        exampleSentence: json['example_sentence'],
        masteryLevel: json['mastery_level'] ?? 'new',
        confidence: json['confidence']?.toDouble(),
      );
}

class QuizQuestion {
  final String wordId;
  final String mode;
  final String prompt;
  final String promptLabel;
  final String correctAnswer;
  final String? hint;
  final List<QuizOption> options;

  QuizQuestion({
    required this.wordId,
    required this.mode,
    required this.prompt,
    required this.promptLabel,
    required this.correctAnswer,
    this.hint,
    required this.options,
  });

  factory QuizQuestion.fromJson(Map<String, dynamic> json) => QuizQuestion(
        wordId: json['word_id'] ?? '',
        mode: json['mode'] ?? '',
        prompt: json['prompt'] ?? '',
        promptLabel: json['prompt_label'] ?? '',
        correctAnswer: json['correct_answer'] ?? '',
        hint: json['hint'],
        options: (json['options'] as List? ?? [])
            .map((o) => QuizOption.fromJson(o))
            .toList(),
      );
}

class QuizOption {
  final String text;
  final bool isCorrect;

  QuizOption({required this.text, required this.isCorrect});

  factory QuizOption.fromJson(Map<String, dynamic> json) => QuizOption(
        text: json['text'] ?? '',
        isCorrect: json['is_correct'] ?? false,
      );
}

class StudyStats {
  final int totalWordsStudied;
  final int totalReviews;
  final double accuracy;
  final int dueToday;
  final MasteryDistribution mastery;
  final StreakInfo streak;
  final Map<String, int> weeklyActivity;

  StudyStats({
    required this.totalWordsStudied,
    required this.totalReviews,
    required this.accuracy,
    required this.dueToday,
    required this.mastery,
    required this.streak,
    required this.weeklyActivity,
  });

  factory StudyStats.fromJson(Map<String, dynamic> json) => StudyStats(
        totalWordsStudied: json['total_words_studied'] ?? 0,
        totalReviews: json['total_reviews'] ?? 0,
        accuracy: (json['accuracy'] ?? 0).toDouble(),
        dueToday: json['due_today'] ?? 0,
        mastery: MasteryDistribution.fromJson(
            json['mastery_distribution'] ?? {}),
        streak: StreakInfo.fromJson(json['streak'] ?? {}),
        weeklyActivity: Map<String, int>.from(json['weekly_activity'] ?? {}),
      );
}

class MasteryDistribution {
  final int newCount;
  final int learning;
  final int review;
  final int mastered;

  int get total => newCount + learning + review + mastered;

  MasteryDistribution({
    required this.newCount,
    required this.learning,
    required this.review,
    required this.mastered,
  });

  factory MasteryDistribution.fromJson(Map<String, dynamic> json) =>
      MasteryDistribution(
        newCount: json['new'] ?? 0,
        learning: json['learning'] ?? 0,
        review: json['review'] ?? 0,
        mastered: json['mastered'] ?? 0,
      );
}

class StreakInfo {
  final int current;
  final int longest;
  final String? lastStudyDate;

  StreakInfo({
    required this.current,
    required this.longest,
    this.lastStudyDate,
  });

  factory StreakInfo.fromJson(Map<String, dynamic> json) => StreakInfo(
        current: json['current'] ?? 0,
        longest: json['longest'] ?? 0,
        lastStudyDate: json['last_study_date'],
      );
}
