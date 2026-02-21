import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:math' as math;
import '../../data/vocab_repository.dart';
import '../../domain/vocab_models.dart';
import 'vocab_provider.dart';

class FlashcardStudyPage extends ConsumerStatefulWidget {
  final String setId;
  final String setName;

  const FlashcardStudyPage({
    super.key,
    required this.setId,
    required this.setName,
  });

  @override
  ConsumerState<FlashcardStudyPage> createState() =>
      _FlashcardStudyPageState();
}

class _FlashcardStudyPageState extends ConsumerState<FlashcardStudyPage>
    with SingleTickerProviderStateMixin {
  List<VocabWord> _words = [];
  int _currentIndex = 0;
  bool _isFlipped = false;
  bool _isLoading = true;
  String? _sessionId;
  late AnimationController _flipController;
  late Animation<double> _flipAnimation;
  DateTime? _cardShownAt;

  // Session stats
  int _totalReviewed = 0;
  int _correctCount = 0;

  @override
  void initState() {
    super.initState();
    _flipController = AnimationController(
      duration: const Duration(milliseconds: 400),
      vsync: this,
    );
    _flipAnimation = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(parent: _flipController, curve: Curves.easeInOut),
    );
    _loadWords();
  }

  Future<void> _loadWords() async {
    final repo = ref.read(vocabRepositoryProvider);
    try {
      // Get review queue + new words
      final reviewWords = await repo.getReviewQueue(setId: widget.setId, limit: 10);
      final newWords = await repo.getNewWords(widget.setId, limit: 10);

      final combined = [...reviewWords, ...newWords];
      combined.shuffle();

      final sessionId = await repo.startSession('flashcard');

      setState(() {
        _words = combined;
        _sessionId = sessionId;
        _isLoading = false;
        _cardShownAt = DateTime.now();
      });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  void _flipCard() {
    if (_isFlipped) {
      _flipController.reverse();
    } else {
      _flipController.forward();
    }
    setState(() => _isFlipped = !_isFlipped);
  }

  Future<void> _rateCard(int quality) async {
    if (_currentIndex >= _words.length) return;

    final word = _words[_currentIndex];
    final timeSpent = _cardShownAt != null
        ? DateTime.now().difference(_cardShownAt!).inMilliseconds
        : 0;

    final repo = ref.read(vocabRepositoryProvider);
    try {
      await repo.reviewWord(
        wordId: word.id,
        quality: quality,
        sessionId: _sessionId,
        timeSpentMs: timeSpent,
      );
    } catch (_) {}

    _totalReviewed++;
    if (quality >= 3) _correctCount++;

    // Reset flip and move to next
    if (_isFlipped) {
      _flipController.reverse();
      _isFlipped = false;
    }

    setState(() {
      _currentIndex++;
      _cardShownAt = DateTime.now();
    });

    // End session if done
    if (_currentIndex >= _words.length) {
      _endSession();
    }
  }

  Future<void> _endSession() async {
    if (_sessionId == null) return;
    final repo = ref.read(vocabRepositoryProvider);
    try {
      await repo.endSession(_sessionId!);
    } catch (_) {}
  }

  @override
  void dispose() {
    _flipController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(title: const Text('Flashcard')),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    if (_words.isEmpty) {
      return Scaffold(
        appBar: AppBar(title: const Text('Flashcard')),
        body: const Center(
          child: Text('Calismak icin kelime bulunamadi.'),
        ),
      );
    }

    // Session complete
    if (_currentIndex >= _words.length) {
      return _buildCompletionScreen();
    }

    final word = _words[_currentIndex];
    final progress = _currentIndex + 1;

    return Scaffold(
      appBar: AppBar(
        title: Text('$progress / ${_words.length}'),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16),
            child: Center(
              child: Text(
                widget.setName,
                style: const TextStyle(fontSize: 14, color: Colors.grey),
              ),
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          // Progress bar
          LinearProgressIndicator(
            value: _currentIndex / _words.length,
            backgroundColor: Colors.grey[200],
          ),
          const SizedBox(height: 24),

          // Flashcard
          Expanded(
            child: GestureDetector(
              onTap: _flipCard,
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24),
                child: AnimatedBuilder(
                  animation: _flipAnimation,
                  builder: (context, child) {
                    final angle = _flipAnimation.value * math.pi;
                    final isFront = angle < math.pi / 2;

                    return Transform(
                      alignment: Alignment.center,
                      transform: Matrix4.identity()
                        ..setEntry(3, 2, 0.001)
                        ..rotateY(angle),
                      child: isFront
                          ? _buildCardFront(word)
                          : Transform(
                              alignment: Alignment.center,
                              transform: Matrix4.identity()..rotateY(math.pi),
                              child: _buildCardBack(word),
                            ),
                    );
                  },
                ),
              ),
            ),
          ),

          // Hint text
          if (!_isFlipped)
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Text(
                'Karti cevirmek icin dokun',
                style: TextStyle(color: Colors.grey[500], fontSize: 14),
              ),
            ),

          // Rating buttons (only when flipped)
          if (_isFlipped) _buildRatingButtons(),

          const SizedBox(height: 24),
        ],
      ),
    );
  }

  Widget _buildCardFront(VocabWord word) {
    return Card(
      elevation: 8,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.translate, size: 48, color: Colors.grey[300]),
            const SizedBox(height: 24),
            Text(
              word.english,
              style: const TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            _buildMasteryChip(word.masteryLevel),
          ],
        ),
      ),
    );
  }

  Widget _buildCardBack(VocabWord word) {
    return Card(
      elevation: 8,
      color: const Color(0xFF6366F1),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.check_circle_outline, size: 48, color: Colors.white.withOpacity(0.5)),
            const SizedBox(height: 24),
            Text(
              word.turkish,
              style: const TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
              textAlign: TextAlign.center,
            ),
            if (word.exampleSentence != null) ...[
              const SizedBox(height: 16),
              Text(
                word.exampleSentence!,
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.white.withOpacity(0.8),
                  fontStyle: FontStyle.italic,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildRatingButtons() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        children: [
          _buildRateButton('Again', 0, Colors.red),
          const SizedBox(width: 8),
          _buildRateButton('Hard', 3, Colors.orange),
          const SizedBox(width: 8),
          _buildRateButton('Good', 4, Colors.blue),
          const SizedBox(width: 8),
          _buildRateButton('Easy', 5, Colors.green),
        ],
      ),
    );
  }

  Widget _buildRateButton(String label, int quality, Color color) {
    return Expanded(
      child: ElevatedButton(
        onPressed: () => _rateCard(quality),
        style: ElevatedButton.styleFrom(
          backgroundColor: color,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        child: Text(label, style: const TextStyle(fontWeight: FontWeight.bold)),
      ),
    );
  }

  Widget _buildMasteryChip(String level) {
    Color color;
    String label;
    switch (level) {
      case 'new':
        color = Colors.grey;
        label = 'Yeni';
        break;
      case 'learning':
        color = Colors.orange;
        label = 'Ogreniyor';
        break;
      case 'review':
        color = Colors.blue;
        label = 'Tekrar';
        break;
      case 'mastered':
        color = Colors.green;
        label = 'Ogrenildi';
        break;
      default:
        color = Colors.grey;
        label = 'Yeni';
    }

    return Chip(
      label: Text(label, style: TextStyle(color: color, fontSize: 12)),
      backgroundColor: color.withOpacity(0.1),
      side: BorderSide(color: color.withOpacity(0.3)),
    );
  }

  Widget _buildCompletionScreen() {
    final accuracy = _totalReviewed > 0
        ? (_correctCount / _totalReviewed * 100).round()
        : 0;

    return Scaffold(
      appBar: AppBar(title: const Text('Tamamlandi!')),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.celebration, size: 80, color: Color(0xFF10B981)),
              const SizedBox(height: 24),
              Text(
                'Tebrikler!',
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const SizedBox(height: 16),
              Text(
                '$_totalReviewed kelime calisildi',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 8),
              Text(
                'Dogruluk: %$accuracy',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: accuracy >= 70 ? Colors.green : Colors.orange,
                    ),
              ),
              const SizedBox(height: 32),
              ElevatedButton.icon(
                onPressed: () => Navigator.of(context).pop(),
                icon: const Icon(Icons.arrow_back),
                label: const Text('Geri Don'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
