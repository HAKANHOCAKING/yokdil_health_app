import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../domain/vocab_models.dart';
import 'vocab_provider.dart';

class ReviewQueuePage extends ConsumerWidget {
  const ReviewQueuePage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final queueAsync = ref.watch(reviewQueueProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Gunluk Tekrar')),
      body: queueAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Hata: $e')),
        data: (words) {
          if (words.isEmpty) {
            return _buildEmptyState(context);
          }
          return _buildWordList(context, words);
        },
      ),
      floatingActionButton: queueAsync.whenOrNull(
        data: (words) {
          if (words.isEmpty) return null;
          return FloatingActionButton.extended(
            onPressed: () {
              // Start flashcard study with review queue
              context.push('/vocab/flashcard?setId=review&setName=Gunluk%20Tekrar');
            },
            icon: const Icon(Icons.play_arrow),
            label: Text('${words.length} Kelime Calis'),
            backgroundColor: const Color(0xFF6366F1),
          );
        },
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.check_circle_outline,
                size: 80, color: Colors.green[300]),
            const SizedBox(height: 24),
            Text(
              'Tebrikler!',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              'Bugun tekrar edilecek kelimeniz yok.\nYeni kelimeler ekleyin veya yarin tekrar gelin.',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey[600], fontSize: 16),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildWordList(BuildContext context, List<VocabWord> words) {
    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemCount: words.length,
      separatorBuilder: (_, __) => const SizedBox(height: 8),
      itemBuilder: (context, index) {
        final word = words[index];
        return _buildWordTile(context, word);
      },
    );
  }

  Widget _buildWordTile(BuildContext context, VocabWord word) {
    return Card(
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: _buildMasteryIcon(word.masteryLevel),
        title: Text(
          word.english,
          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
        ),
        subtitle: Text(
          word.turkish,
          style: TextStyle(color: Colors.grey[600]),
        ),
        trailing: Icon(Icons.arrow_forward_ios,
            size: 16, color: Colors.grey[400]),
      ),
    );
  }

  Widget _buildMasteryIcon(String level) {
    Color color;
    IconData icon;
    switch (level) {
      case 'learning':
        color = Colors.orange;
        icon = Icons.school;
        break;
      case 'review':
        color = Colors.blue;
        icon = Icons.refresh;
        break;
      case 'mastered':
        color = Colors.green;
        icon = Icons.star;
        break;
      default:
        color = Colors.grey;
        icon = Icons.fiber_new;
    }

    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Icon(icon, color: color, size: 24),
    );
  }
}
