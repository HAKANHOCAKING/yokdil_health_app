import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'vocab_provider.dart';

class StudyModePage extends ConsumerWidget {
  final String setId;
  final String setName;

  const StudyModePage({
    super.key,
    required this.setId,
    required this.setName,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: Text(setName)),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Calisma Modu Sec',
              style: Theme.of(context)
                  .textTheme
                  .headlineSmall
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              'Kelimelerini nasil calismak istiyorsun?',
              style: Theme.of(context)
                  .textTheme
                  .bodyLarge
                  ?.copyWith(color: Colors.grey[600]),
            ),
            const SizedBox(height: 24),
            _buildModeCard(
              context,
              title: 'Flashcard',
              subtitle: 'Kart cevirme ile kelime calis',
              icon: Icons.style,
              color: const Color(0xFF6366F1),
              onTap: () => context.push(
                '/vocab/flashcard?setId=$setId&setName=$setName',
              ),
            ),
            const SizedBox(height: 12),
            _buildModeCard(
              context,
              title: 'Quiz: EN -> TR',
              subtitle: 'Ingilizce kelime, Turkce anlam sec',
              icon: Icons.translate,
              color: const Color(0xFF8B5CF6),
              onTap: () => context.push(
                '/vocab/quiz?setId=$setId&mode=en_tr',
              ),
            ),
            const SizedBox(height: 12),
            _buildModeCard(
              context,
              title: 'Quiz: TR -> EN',
              subtitle: 'Turkce anlam, Ingilizce kelime sec',
              icon: Icons.g_translate,
              color: const Color(0xFF10B981),
              onTap: () => context.push(
                '/vocab/quiz?setId=$setId&mode=tr_en',
              ),
            ),
            const SizedBox(height: 12),
            _buildModeCard(
              context,
              title: 'Bosluk Doldurma',
              subtitle: 'Cumle icinde dogru kelimeyi bul',
              icon: Icons.edit_note,
              color: const Color(0xFFF59E0B),
              onTap: () => context.push(
                '/vocab/quiz?setId=$setId&mode=fill_blank',
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildModeCard(
    BuildContext context, {
    required String title,
    required String subtitle,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(icon, color: color, size: 32),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: Theme.of(context)
                          .textTheme
                          .titleMedium
                          ?.copyWith(fontWeight: FontWeight.bold),
                    ),
                    Text(
                      subtitle,
                      style: Theme.of(context)
                          .textTheme
                          .bodyMedium
                          ?.copyWith(color: Colors.grey[600]),
                    ),
                  ],
                ),
              ),
              Icon(Icons.arrow_forward_ios, color: Colors.grey[400], size: 20),
            ],
          ),
        ),
      ),
    );
  }
}
