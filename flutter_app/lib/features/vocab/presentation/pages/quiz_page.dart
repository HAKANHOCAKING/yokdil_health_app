import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/vocab_repository.dart';
import '../../domain/vocab_models.dart';
import 'vocab_provider.dart';

class QuizPage extends ConsumerStatefulWidget {
  final String setId;
  final String mode; // en_tr, tr_en, fill_blank

  const QuizPage({
    super.key,
    required this.setId,
    required this.mode,
  });

  @override
  ConsumerState<QuizPage> createState() => _QuizPageState();
}

class _QuizPageState extends ConsumerState<QuizPage> {
  List<QuizQuestion> _questions = [];
  int _currentIndex = 0;
  bool _isLoading = true;
  String? _sessionId;
  int? _selectedOptionIndex;
  bool _answered = false;
  DateTime? _questionShownAt;

  // Stats
  int _correctCount = 0;
  int _totalAnswered = 0;

  // Timer
  int _timeLeft = 30;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _loadQuiz();
  }

  Future<void> _loadQuiz() async {
    final repo = ref.read(vocabRepositoryProvider);
    try {
      final questions = await repo.generateQuiz(
        setId: widget.setId,
        mode: widget.mode,
        count: 10,
      );
      final sessionId = await repo.startSession('quiz_${widget.mode}');

      setState(() {
        _questions = questions;
        _sessionId = sessionId;
        _isLoading = false;
        _questionShownAt = DateTime.now();
      });
      _startTimer();
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  void _startTimer() {
    _timer?.cancel();
    _timeLeft = 30;
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_timeLeft > 0) {
        setState(() => _timeLeft--);
      } else {
        timer.cancel();
        if (!_answered) _selectOption(-1); // Time's up = wrong
      }
    });
  }

  Future<void> _selectOption(int index) async {
    if (_answered) return;
    _timer?.cancel();

    final question = _questions[_currentIndex];
    final isCorrect =
        index >= 0 && question.options[index].isCorrect;
    final quality = isCorrect ? 4 : 0; // Good or Again

    final timeSpent = _questionShownAt != null
        ? DateTime.now().difference(_questionShownAt!).inMilliseconds
        : 0;

    // Record review
    final repo = ref.read(vocabRepositoryProvider);
    try {
      await repo.reviewWord(
        wordId: question.wordId,
        quality: quality,
        sessionId: _sessionId,
        timeSpentMs: timeSpent,
      );
    } catch (_) {}

    _totalAnswered++;
    if (isCorrect) _correctCount++;

    setState(() {
      _selectedOptionIndex = index;
      _answered = true;
    });
  }

  void _nextQuestion() {
    if (_currentIndex + 1 >= _questions.length) {
      _endSession();
      setState(() => _currentIndex++);
      return;
    }

    setState(() {
      _currentIndex++;
      _selectedOptionIndex = null;
      _answered = false;
      _questionShownAt = DateTime.now();
    });
    _startTimer();
  }

  Future<void> _endSession() async {
    if (_sessionId == null) return;
    try {
      await ref.read(vocabRepositoryProvider).endSession(_sessionId!);
    } catch (_) {}
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  String get _modeTitle {
    switch (widget.mode) {
      case 'en_tr':
        return 'EN -> TR Quiz';
      case 'tr_en':
        return 'TR -> EN Quiz';
      case 'fill_blank':
        return 'Bosluk Doldurma';
      default:
        return 'Quiz';
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(title: Text(_modeTitle)),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    if (_questions.isEmpty) {
      return Scaffold(
        appBar: AppBar(title: Text(_modeTitle)),
        body: const Center(
          child: Text('Quiz olusturmak icin yeterli kelime yok (en az 4).'),
        ),
      );
    }

    if (_currentIndex >= _questions.length) {
      return _buildResultScreen();
    }

    final question = _questions[_currentIndex];

    return Scaffold(
      appBar: AppBar(
        title: Text('${_currentIndex + 1} / ${_questions.length}'),
        actions: [
          // Timer
          Padding(
            padding: const EdgeInsets.only(right: 16),
            child: Center(
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: _timeLeft <= 10
                      ? Colors.red.withOpacity(0.1)
                      : Colors.grey.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.timer,
                      size: 18,
                      color: _timeLeft <= 10 ? Colors.red : Colors.grey,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      '${_timeLeft}s',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: _timeLeft <= 10 ? Colors.red : Colors.grey[700],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          // Progress
          LinearProgressIndicator(
            value: _currentIndex / _questions.length,
            backgroundColor: Colors.grey[200],
          ),

          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Score
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      _buildScoreChip(
                          Icons.check_circle, '$_correctCount', Colors.green),
                      const SizedBox(width: 12),
                      _buildScoreChip(
                          Icons.cancel,
                          '${_totalAnswered - _correctCount}',
                          Colors.red),
                    ],
                  ),
                  const SizedBox(height: 24),

                  // Question prompt
                  Text(
                    question.promptLabel,
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey[600],
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Card(
                    color: const Color(0xFFF8F9FA),
                    child: Padding(
                      padding: const EdgeInsets.all(20),
                      child: Center(
                        child: Text(
                          question.prompt,
                          style: const TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ),
                  ),

                  // Hint for fill-blank
                  if (question.hint != null) ...[
                    const SizedBox(height: 8),
                    Center(
                      child: Text(
                        'Ipucu: ${question.hint}',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.blue[600],
                          fontStyle: FontStyle.italic,
                        ),
                      ),
                    ),
                  ],

                  const SizedBox(height: 24),

                  // Options
                  ...List.generate(question.options.length, (i) {
                    return _buildOptionTile(question, i);
                  }),

                  // Next button
                  if (_answered) ...[
                    const SizedBox(height: 24),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: _nextQuestion,
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 16),
                        ),
                        child: Text(
                          _currentIndex + 1 < _questions.length
                              ? 'Sonraki Soru'
                              : 'Sonuclari Gor',
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildOptionTile(QuizQuestion question, int index) {
    final option = question.options[index];
    Color? bgColor;
    Color? borderColor;
    IconData? trailingIcon;

    if (_answered) {
      if (option.isCorrect) {
        bgColor = Colors.green.withOpacity(0.1);
        borderColor = Colors.green;
        trailingIcon = Icons.check_circle;
      } else if (index == _selectedOptionIndex && !option.isCorrect) {
        bgColor = Colors.red.withOpacity(0.1);
        borderColor = Colors.red;
        trailingIcon = Icons.cancel;
      }
    } else if (index == _selectedOptionIndex) {
      bgColor = const Color(0xFF6366F1).withOpacity(0.1);
      borderColor = const Color(0xFF6366F1);
    }

    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: InkWell(
        onTap: _answered ? null : () => _selectOption(index),
        borderRadius: BorderRadius.circular(12),
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: bgColor ?? Colors.white,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: borderColor ?? Colors.grey[300]!,
              width: borderColor != null ? 2 : 1,
            ),
          ),
          child: Row(
            children: [
              Container(
                width: 32,
                height: 32,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: Colors.grey[200],
                ),
                child: Center(
                  child: Text(
                    String.fromCharCode(65 + index), // A, B, C, D
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  option.text,
                  style: const TextStyle(fontSize: 16),
                ),
              ),
              if (trailingIcon != null)
                Icon(trailingIcon,
                    color: option.isCorrect ? Colors.green : Colors.red),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildScoreChip(IconData icon, String value, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 18, color: color),
          const SizedBox(width: 4),
          Text(value,
              style: TextStyle(fontWeight: FontWeight.bold, color: color)),
        ],
      ),
    );
  }

  Widget _buildResultScreen() {
    final accuracy = _totalAnswered > 0
        ? (_correctCount / _totalAnswered * 100).round()
        : 0;

    return Scaffold(
      appBar: AppBar(title: const Text('Quiz Sonuclari')),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                accuracy >= 70 ? Icons.emoji_events : Icons.trending_up,
                size: 80,
                color: accuracy >= 70
                    ? const Color(0xFFF59E0B)
                    : const Color(0xFF6366F1),
              ),
              const SizedBox(height: 24),
              Text(
                accuracy >= 70 ? 'Harika!' : 'Devam Et!',
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const SizedBox(height: 24),
              _buildStatRow('Toplam Soru', '$_totalAnswered'),
              _buildStatRow('Dogru', '$_correctCount'),
              _buildStatRow('Yanlis', '${_totalAnswered - _correctCount}'),
              _buildStatRow('Dogruluk', '%$accuracy'),
              const SizedBox(height: 32),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => Navigator.of(context).pop(),
                      icon: const Icon(Icons.arrow_back),
                      label: const Text('Geri Don'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () {
                        setState(() {
                          _currentIndex = 0;
                          _correctCount = 0;
                          _totalAnswered = 0;
                          _answered = false;
                          _selectedOptionIndex = null;
                          _isLoading = true;
                        });
                        _loadQuiz();
                      },
                      icon: const Icon(Icons.refresh),
                      label: const Text('Tekrar'),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 16, color: Colors.grey)),
          Text(value,
              style:
                  const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}
