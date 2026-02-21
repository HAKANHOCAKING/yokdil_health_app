import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../domain/vocab_models.dart';
import 'vocab_provider.dart';

class VocabSetsPage extends ConsumerWidget {
  const VocabSetsPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final setsAsync = ref.watch(vocabSetsProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Kelime Setleri')),
      body: setsAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Hata: $e')),
        data: (sets) {
          if (sets.isEmpty) {
            return const Center(
              child: Text('Henuz kelime seti eklenmedi.'),
            );
          }

          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: sets.length,
            separatorBuilder: (_, __) => const SizedBox(height: 8),
            itemBuilder: (context, index) {
              final set = sets[index];
              return _buildSetCard(context, set);
            },
          );
        },
      ),
    );
  }

  Widget _buildSetCard(BuildContext context, VocabSet set) {
    return Card(
      child: InkWell(
        onTap: () => context.push(
          '/vocab/study?setId=${set.id}&setName=${Uri.encodeComponent(set.name)}',
        ),
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFF6366F1).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.library_books,
                    color: Color(0xFF6366F1), size: 28),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      set.name,
                      style: Theme.of(context)
                          .textTheme
                          .titleMedium
                          ?.copyWith(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${set.wordCount} kelime',
                      style: TextStyle(color: Colors.grey[600]),
                    ),
                  ],
                ),
              ),
              Icon(Icons.arrow_forward_ios,
                  color: Colors.grey[400], size: 20),
            ],
          ),
        ),
      ),
    );
  }
}
