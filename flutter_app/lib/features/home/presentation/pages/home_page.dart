import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../auth/presentation/providers/auth_provider.dart';

class HomePage extends ConsumerWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);
    final user = authState.user;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Senior Words'),
        actions: [
          IconButton(
            icon: const Icon(Icons.person),
            onPressed: () => _showProfileBottomSheet(context, ref),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Welcome Card
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Hos geldin, ${user?.fullName ?? ""}!',
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Bugün hangi modda calismak istersin?',
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                            color: Colors.grey[600],
                          ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // --- Kelime Ogrenme ---
            Text(
              'Kelime Ogrenme',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 16),

            _buildModeCard(
              context,
              title: 'Gunluk Tekrar',
              subtitle: 'Bugün tekrar edilecek kelimeler',
              icon: Icons.today,
              color: const Color(0xFFF59E0B),
              onTap: () => context.push('/vocab/review'),
            ),
            const SizedBox(height: 12),

            _buildModeCard(
              context,
              title: 'Kelime Setleri',
              subtitle: 'Setlerden calis: flashcard, quiz, bosluk doldurma',
              icon: Icons.library_books,
              color: const Color(0xFF6366F1),
              onTap: () => context.push('/vocab/sets'),
            ),
            const SizedBox(height: 12),

            _buildModeCard(
              context,
              title: 'Ilerleme Paneli',
              subtitle: 'Mastery, streak, dogruluk orani',
              icon: Icons.bar_chart,
              color: const Color(0xFF10B981),
              onTap: () => context.push('/vocab/dashboard'),
            ),
            const SizedBox(height: 24),

            // --- Sinav Hazirligi ---
            Text(
              'Sinav Hazirligi',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 16),

            _buildModeCard(
              context,
              title: 'Sinav Modu',
              subtitle: 'Gercek sinav kosullarinda pratik yap',
              icon: Icons.timer,
              color: const Color(0xFF6366F1),
              onTap: () => context.push('/session/exam'),
            ),
            const SizedBox(height: 12),

            _buildModeCard(
              context,
              title: 'Kocluk Modu',
              subtitle: 'Aninda aciklama ve tuzak analizi',
              icon: Icons.school,
              color: const Color(0xFF8B5CF6),
              onTap: () => context.push('/session/coaching'),
            ),
            const SizedBox(height: 12),

            _buildModeCard(
              context,
              title: 'Hizli Tekrar',
              subtitle: 'Yanlis sorular ve zayif noktalar',
              icon: Icons.flash_on,
              color: const Color(0xFFF59E0B),
              onTap: () => context.push('/session/quick_review'),
            ),
            const SizedBox(height: 12),

            _buildModeCard(
              context,
              title: 'Akilli Karisim',
              subtitle: 'AI tarafindan onerilen sorular',
              icon: Icons.auto_awesome,
              color: const Color(0xFF10B981),
              onTap: () => context.push('/session/smart_mix'),
            ),
            const SizedBox(height: 24),

            // Quick Actions
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => context.push('/questions'),
                    icon: const Icon(Icons.question_answer),
                    label: const Text('Soru Bankasi'),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => context.push('/analytics'),
                    icon: const Icon(Icons.bar_chart),
                    label: const Text('Istatistikler'),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                  ),
                ),
              ],
            ),

            // Admin button (if admin)
            if (user?.isAdmin == true) ...[
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: () => context.push('/admin/vocab'),
                  icon: const Icon(Icons.admin_panel_settings),
                  label: const Text('Admin: Kelime Yonetimi'),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                ),
              ),
            ],
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
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    Text(
                      subtitle,
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: Colors.grey[600],
                          ),
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

  void _showProfileBottomSheet(BuildContext context, WidgetRef ref) {
    final user = ref.read(authProvider).user;

    showModalBottomSheet(
      context: context,
      builder: (context) {
        return Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Profil',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const SizedBox(height: 16),
              ListTile(
                leading: const Icon(Icons.person),
                title: Text(user?.fullName ?? ''),
                subtitle: Text(user?.email ?? ''),
              ),
              ListTile(
                leading: const Icon(Icons.badge),
                title: const Text('Rol'),
                subtitle: Text(
                  user?.isStudent == true
                      ? 'Ogrenci'
                      : user?.isTeacher == true
                          ? 'Ogretmen'
                          : 'Admin',
                ),
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: () async {
                    await ref.read(authProvider.notifier).logout();
                    if (context.mounted) {
                      context.go('/login');
                    }
                  },
                  icon: const Icon(Icons.logout),
                  label: const Text('Cikis Yap'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red,
                    foregroundColor: Colors.white,
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
