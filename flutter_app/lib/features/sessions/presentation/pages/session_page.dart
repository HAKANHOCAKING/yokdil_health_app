import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class SessionPage extends ConsumerStatefulWidget {
  final String mode;

  const SessionPage({super.key, required this.mode});

  @override
  ConsumerState<SessionPage> createState() => _SessionPageState();
}

class _SessionPageState extends ConsumerState<SessionPage> {
  int _currentQuestionIndex = 0;
  final int _totalQuestions = 10;

  @override
  Widget build(BuildContext context) {
    final modeTitle = _getModeTitle(widget.mode);

    return Scaffold(
      appBar: AppBar(
        title: Text(modeTitle),
        actions: [
          if (widget.mode == 'exam')
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Center(
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.red.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: const Row(
                    children: [
                      Icon(Icons.timer, size: 16, color: Colors.red),
                      SizedBox(width: 4),
                      Text(
                        '45:00',
                        style: TextStyle(
                          color: Colors.red,
                          fontWeight: FontWeight.bold,
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
          // Progress Bar
          LinearProgressIndicator(
            value: (_currentQuestionIndex + 1) / _totalQuestions,
            backgroundColor: Colors.grey[200],
          ),

          // Question Number
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Soru ${_currentQuestionIndex + 1}/$_totalQuestions',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                if (widget.mode == 'coaching')
                  TextButton.icon(
                    onPressed: () {
                      // TODO: Show hint
                    },
                    icon: const Icon(Icons.lightbulb_outline, size: 20),
                    label: const Text('İpucu'),
                  ),
              ],
            ),
          ),

          // Question Content (placeholder)
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(20),
                      child: Text(
                        'Recent studies suggest that regular physical activity ------- the risk of developing chronic diseases.',
                        style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                              height: 1.5,
                            ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Placeholder options
                  _buildOption('A', 'reduces'),
                  _buildOption('B', 'increases'),
                  _buildOption('C', 'prevents'),
                  _buildOption('D', 'eliminates'),
                  _buildOption('E', 'avoids'),
                ],
              ),
            ),
          ),

          // Navigation Buttons
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                if (_currentQuestionIndex > 0)
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {
                        setState(() {
                          _currentQuestionIndex--;
                        });
                      },
                      icon: const Icon(Icons.arrow_back),
                      label: const Text('Önceki'),
                    ),
                  ),
                if (_currentQuestionIndex > 0) const SizedBox(width: 12),
                Expanded(
                  flex: 2,
                  child: ElevatedButton.icon(
                    onPressed: () {
                      if (_currentQuestionIndex < _totalQuestions - 1) {
                        setState(() {
                          _currentQuestionIndex++;
                        });
                      } else {
                        // TODO: Complete session
                        _showCompletionDialog();
                      }
                    },
                    icon: Icon(
                      _currentQuestionIndex < _totalQuestions - 1
                          ? Icons.arrow_forward
                          : Icons.check,
                    ),
                    label: Text(
                      _currentQuestionIndex < _totalQuestions - 1
                          ? 'Sonraki'
                          : 'Bitir',
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildOption(String letter, String text) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: InkWell(
        onTap: () {
          // TODO: Select option
        },
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                width: 32,
                height: 32,
                decoration: BoxDecoration(
                  color: Colors.grey[300],
                  shape: BoxShape.circle,
                ),
                child: Center(
                  child: Text(
                    letter,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Text(text, style: const TextStyle(fontSize: 16)),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _getModeTitle(String mode) {
    switch (mode) {
      case 'exam':
        return 'Sınav Modu';
      case 'coaching':
        return 'Koçluk Modu';
      case 'quick_review':
        return 'Hızlı Tekrar';
      case 'smart_mix':
        return 'Akıllı Karışım';
      default:
        return 'Çalışma';
    }
  }

  void _showCompletionDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) {
        return AlertDialog(
          title: const Text('Tebrikler! 🎉'),
          content: const Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Çalışmayı tamamladınız!'),
              SizedBox(height: 16),
              Text('Toplam Soru: 10'),
              Text('Doğru: 7'),
              Text('Yanlış: 3'),
              Text('Başarı Oranı: %70'),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(context);
                Navigator.pop(context);
              },
              child: const Text('Ana Sayfaya Dön'),
            ),
          ],
        );
      },
    );
  }
}
