import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../domain/vocab_models.dart';
import 'vocab_provider.dart';

class ProgressDashboardPage extends ConsumerWidget {
  const ProgressDashboardPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final statsAsync = ref.watch(studyStatsProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Ilerleme Paneli')),
      body: statsAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Hata: $e')),
        data: (stats) => _buildDashboard(context, stats),
      ),
    );
  }

  Widget _buildDashboard(BuildContext context, StudyStats stats) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Streak Card
          _buildStreakCard(context, stats.streak),
          const SizedBox(height: 16),

          // Quick Stats Row
          Row(
            children: [
              Expanded(
                child: _buildStatCard(
                  context,
                  icon: Icons.library_books,
                  label: 'Toplam Kelime',
                  value: '${stats.totalWordsStudied}',
                  color: const Color(0xFF6366F1),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildStatCard(
                  context,
                  icon: Icons.repeat,
                  label: 'Toplam Tekrar',
                  value: '${stats.totalReviews}',
                  color: const Color(0xFF8B5CF6),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _buildStatCard(
                  context,
                  icon: Icons.check_circle,
                  label: 'Dogruluk',
                  value: '%${stats.accuracy.round()}',
                  color: const Color(0xFF10B981),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildStatCard(
                  context,
                  icon: Icons.today,
                  label: 'Bugun Tekrar',
                  value: '${stats.dueToday}',
                  color: const Color(0xFFF59E0B),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),

          // Mastery Distribution
          Text(
            'Ogrenme Durumu',
            style: Theme.of(context)
                .textTheme
                .titleLarge
                ?.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          _buildMasteryChart(context, stats.mastery),
          const SizedBox(height: 24),

          // Mastery Legend
          _buildMasteryLegend(context, stats.mastery),
          const SizedBox(height: 24),

          // Weekly Activity
          Text(
            'Haftalik Aktivite',
            style: Theme.of(context)
                .textTheme
                .titleLarge
                ?.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          _buildWeeklyChart(context, stats.weeklyActivity),
        ],
      ),
    );
  }

  Widget _buildStreakCard(BuildContext context, StreakInfo streak) {
    return Card(
      color: streak.current > 0 ? const Color(0xFFFFF7ED) : null,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFFF59E0B).withOpacity(0.2),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(Icons.local_fire_department,
                  color: Color(0xFFF59E0B), size: 36),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '${streak.current} Gun Seri',
                    style: Theme.of(context)
                        .textTheme
                        .titleLarge
                        ?.copyWith(fontWeight: FontWeight.bold),
                  ),
                  Text(
                    'En uzun: ${streak.longest} gun',
                    style: TextStyle(color: Colors.grey[600]),
                  ),
                ],
              ),
            ),
            if (streak.current >= 7)
              const Icon(Icons.emoji_events,
                  color: Color(0xFFF59E0B), size: 32),
          ],
        ),
      ),
    );
  }

  Widget _buildStatCard(
    BuildContext context, {
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: color, size: 28),
            const SizedBox(height: 8),
            Text(
              value,
              style: Theme.of(context)
                  .textTheme
                  .headlineSmall
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
            Text(
              label,
              style: TextStyle(color: Colors.grey[600], fontSize: 13),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMasteryChart(BuildContext context, MasteryDistribution mastery) {
    if (mastery.total == 0) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Center(
            child: Text(
              'Henuz kelime calismadin.',
              style: TextStyle(color: Colors.grey[500]),
            ),
          ),
        ),
      );
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: SizedBox(
          height: 200,
          child: PieChart(
            PieChartData(
              sectionsSpace: 2,
              centerSpaceRadius: 40,
              sections: [
                if (mastery.newCount > 0)
                  PieChartSectionData(
                    value: mastery.newCount.toDouble(),
                    color: Colors.grey,
                    title: '${mastery.newCount}',
                    titleStyle: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 14),
                    radius: 60,
                  ),
                if (mastery.learning > 0)
                  PieChartSectionData(
                    value: mastery.learning.toDouble(),
                    color: Colors.orange,
                    title: '${mastery.learning}',
                    titleStyle: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 14),
                    radius: 60,
                  ),
                if (mastery.review > 0)
                  PieChartSectionData(
                    value: mastery.review.toDouble(),
                    color: Colors.blue,
                    title: '${mastery.review}',
                    titleStyle: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 14),
                    radius: 60,
                  ),
                if (mastery.mastered > 0)
                  PieChartSectionData(
                    value: mastery.mastered.toDouble(),
                    color: Colors.green,
                    title: '${mastery.mastered}',
                    titleStyle: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 14),
                    radius: 60,
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildMasteryLegend(
      BuildContext context, MasteryDistribution mastery) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _buildLegendRow('Yeni', mastery.newCount, Colors.grey),
            const Divider(),
            _buildLegendRow('Ogreniyor', mastery.learning, Colors.orange),
            const Divider(),
            _buildLegendRow('Tekrarda', mastery.review, Colors.blue),
            const Divider(),
            _buildLegendRow('Ogrenildi', mastery.mastered, Colors.green),
          ],
        ),
      ),
    );
  }

  Widget _buildLegendRow(String label, int count, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Container(
            width: 16,
            height: 16,
            decoration: BoxDecoration(
              color: color,
              borderRadius: BorderRadius.circular(4),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(child: Text(label)),
          Text('$count',
              style: const TextStyle(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _buildWeeklyChart(
      BuildContext context, Map<String, int> weeklyActivity) {
    // Generate last 7 days
    final today = DateTime.now();
    final days = List.generate(
        7, (i) => today.subtract(Duration(days: 6 - i)));
    final dayLabels = ['Pzt', 'Sal', 'Car', 'Per', 'Cum', 'Cmt', 'Paz'];

    final barGroups = days.asMap().entries.map((entry) {
      final i = entry.key;
      final day = entry.value;
      final dateStr =
          '${day.year}-${day.month.toString().padLeft(2, '0')}-${day.day.toString().padLeft(2, '0')}';
      final count = weeklyActivity[dateStr] ?? 0;

      return BarChartGroupData(
        x: i,
        barRods: [
          BarChartRodData(
            toY: count.toDouble(),
            color: const Color(0xFF6366F1),
            width: 24,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(6)),
          ),
        ],
      );
    }).toList();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: SizedBox(
          height: 200,
          child: BarChart(
            BarChartData(
              alignment: BarChartAlignment.spaceAround,
              maxY: (weeklyActivity.values.isEmpty
                      ? 10
                      : weeklyActivity.values
                          .reduce((a, b) => a > b ? a : b))
                  .toDouble() *
                  1.2 + 1,
              barGroups: barGroups,
              titlesData: FlTitlesData(
                topTitles:
                    const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                rightTitles:
                    const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                leftTitles: const AxisTitles(
                  sideTitles: SideTitles(showTitles: true, reservedSize: 30),
                ),
                bottomTitles: AxisTitles(
                  sideTitles: SideTitles(
                    showTitles: true,
                    getTitlesWidget: (value, meta) {
                      final day = days[value.toInt()];
                      return Padding(
                        padding: const EdgeInsets.only(top: 4),
                        child: Text(
                          dayLabels[day.weekday - 1],
                          style:
                              const TextStyle(fontSize: 12, color: Colors.grey),
                        ),
                      );
                    },
                  ),
                ),
              ),
              borderData: FlBorderData(show: false),
              gridData: const FlGridData(show: true, drawVerticalLine: false),
            ),
          ),
        ),
      ),
    );
  }
}
