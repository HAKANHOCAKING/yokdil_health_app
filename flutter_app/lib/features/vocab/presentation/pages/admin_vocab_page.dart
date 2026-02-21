import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/vocab_repository.dart';
import '../../domain/vocab_models.dart';
import 'vocab_provider.dart';

class AdminVocabPage extends ConsumerStatefulWidget {
  const AdminVocabPage({super.key});

  @override
  ConsumerState<AdminVocabPage> createState() => _AdminVocabPageState();
}

class _AdminVocabPageState extends ConsumerState<AdminVocabPage>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Kelime Yonetimi'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Setler', icon: Icon(Icons.library_books)),
            Tab(text: 'OCR Tarama', icon: Icon(Icons.document_scanner)),
            Tab(text: 'Toplu Ekle', icon: Icon(Icons.upload_file)),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _SetManagementTab(),
          _OcrScanTab(),
          _BulkImportTab(),
        ],
      ),
    );
  }
}

// --- Tab 1: Set Management ---

class _SetManagementTab extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final setsAsync = ref.watch(vocabSetsProvider);

    return setsAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => Center(child: Text('Hata: $e')),
      data: (sets) {
        if (sets.isEmpty) {
          return const Center(child: Text('Henuz set yok.'));
        }

        return ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: sets.length,
          itemBuilder: (context, index) {
            final set = sets[index];
            return Card(
              child: ListTile(
                title: Text(set.name,
                    style: const TextStyle(fontWeight: FontWeight.bold)),
                subtitle: Text('${set.wordCount} kelime - ${set.status}'),
                trailing: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    IconButton(
                      icon: const Icon(Icons.edit, color: Colors.blue),
                      onPressed: () =>
                          _showEditSetDialog(context, ref, set),
                    ),
                    IconButton(
                      icon: const Icon(Icons.add_circle, color: Colors.green),
                      onPressed: () =>
                          _showAddWordDialog(context, ref, set.id),
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  void _showEditSetDialog(BuildContext context, WidgetRef ref, VocabSet set) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(set.name),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Kelime Sayisi: ${set.wordCount}'),
            Text('Durum: ${set.status}'),
            Text('Olusturulma: ${set.createdAt}'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Kapat'),
          ),
        ],
      ),
    );
  }

  void _showAddWordDialog(BuildContext context, WidgetRef ref, String setId) {
    final enController = TextEditingController();
    final trController = TextEditingController();
    final exampleController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Kelime Ekle'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: enController,
                decoration: const InputDecoration(labelText: 'Ingilizce'),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: trController,
                decoration: const InputDecoration(labelText: 'Turkce'),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: exampleController,
                decoration:
                    const InputDecoration(labelText: 'Ornek Cumle (Opsiyonel)'),
                maxLines: 2,
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Iptal'),
          ),
          ElevatedButton(
            onPressed: () async {
              if (enController.text.isEmpty || trController.text.isEmpty) return;
              // TODO: Call API to add word
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Kelime eklendi!')),
              );
            },
            child: const Text('Ekle'),
          ),
        ],
      ),
    );
  }
}

// --- Tab 2: OCR Scan ---

class _OcrScanTab extends StatefulWidget {
  @override
  State<_OcrScanTab> createState() => _OcrScanTabState();
}

class _OcrScanTabState extends State<_OcrScanTab> {
  List<Map<String, dynamic>> _ocrDrafts = [];
  bool _isScanning = false;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'OCR Kelime Tarama',
                    style: Theme.of(context)
                        .textTheme
                        .titleMedium
                        ?.copyWith(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'PDF sayfalarini tarayarak kelime ciftlerini otomatik cikarir.',
                    style: TextStyle(color: Colors.grey[600]),
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: _isScanning ? null : _startScan,
                      icon: _isScanning
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child:
                                  CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.document_scanner),
                      label:
                          Text(_isScanning ? 'Taraniyor...' : 'Taramayi Baslat'),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          if (_ocrDrafts.isNotEmpty) ...[
            Text(
              '${_ocrDrafts.length} kelime bulundu',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Expanded(
              child: ListView.builder(
                itemCount: _ocrDrafts.length,
                itemBuilder: (context, index) {
                  final draft = _ocrDrafts[index];
                  final confidence = (draft['confidence'] ?? 0.0) as double;
                  return _buildDraftTile(draft, confidence, index);
                },
              ),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => setState(() => _ocrDrafts.clear()),
                    child: const Text('Temizle'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton(
                    onPressed: _approveAll,
                    child: const Text('Tumunu Onayla'),
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildDraftTile(
      Map<String, dynamic> draft, double confidence, int index) {
    Color confColor;
    if (confidence >= 0.8) {
      confColor = Colors.green;
    } else if (confidence >= 0.5) {
      confColor = Colors.orange;
    } else {
      confColor = Colors.red;
    }

    return Card(
      child: ListTile(
        leading: Container(
          width: 8,
          height: 40,
          decoration: BoxDecoration(
            color: confColor,
            borderRadius: BorderRadius.circular(4),
          ),
        ),
        title: Text(
          '${draft["english"]} - ${draft["turkish"]}',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text(
          'Guven: ${(confidence * 100).round()}% | Sayfa: ${draft["page"] ?? "?"}',
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(
              icon: const Icon(Icons.edit, size: 20),
              onPressed: () => _editDraft(index),
            ),
            IconButton(
              icon: const Icon(Icons.delete, size: 20, color: Colors.red),
              onPressed: () {
                setState(() => _ocrDrafts.removeAt(index));
              },
            ),
          ],
        ),
      ),
    );
  }

  void _startScan() {
    setState(() => _isScanning = true);
    // Simulate OCR scan (in real app, would call API)
    Future.delayed(const Duration(seconds: 2), () {
      setState(() {
        _isScanning = false;
        _ocrDrafts = [
          {'english': 'abundant', 'turkish': 'bol', 'confidence': 0.92, 'page': 1},
          {'english': 'chronic', 'turkish': 'kronik', 'confidence': 0.88, 'page': 1},
          {'english': 'diagnosis', 'turkish': 'teshis', 'confidence': 0.95, 'page': 2},
          {'english': 'symptom', 'turkish': 'belirti', 'confidence': 0.78, 'page': 2},
          {'english': 'treatment', 'turkish': 'tedavi', 'confidence': 0.85, 'page': 3},
        ];
      });
    });
  }

  void _editDraft(int index) {
    final draft = _ocrDrafts[index];
    final enController = TextEditingController(text: draft['english']);
    final trController = TextEditingController(text: draft['turkish']);

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Kelime Duzenle'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: enController,
              decoration: const InputDecoration(labelText: 'Ingilizce'),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: trController,
              decoration: const InputDecoration(labelText: 'Turkce'),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Iptal'),
          ),
          ElevatedButton(
            onPressed: () {
              setState(() {
                _ocrDrafts[index] = {
                  ..._ocrDrafts[index],
                  'english': enController.text,
                  'turkish': trController.text,
                  'confidence': 1.0, // Manual edit = full confidence
                };
              });
              Navigator.pop(context);
            },
            child: const Text('Kaydet'),
          ),
        ],
      ),
    );
  }

  void _approveAll() {
    // TODO: Call bulk import API
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
          content: Text('${_ocrDrafts.length} kelime onaylandi ve eklendi!')),
    );
    setState(() => _ocrDrafts.clear());
  }
}

// --- Tab 3: Bulk Import ---

class _BulkImportTab extends StatefulWidget {
  @override
  State<_BulkImportTab> createState() => _BulkImportTabState();
}

class _BulkImportTabState extends State<_BulkImportTab> {
  final _setNameController = TextEditingController();
  final _jsonController = TextEditingController();
  bool _isImporting = false;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Toplu JSON Import',
                    style: Theme.of(context)
                        .textTheme
                        .titleMedium
                        ?.copyWith(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    controller: _setNameController,
                    decoration: const InputDecoration(
                      labelText: 'Set Adi',
                      hintText: 'ornek: YDS 2024 Kelimeleri',
                    ),
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    controller: _jsonController,
                    decoration: const InputDecoration(
                      labelText: 'JSON Verisi',
                      hintText:
                          '[{"english":"word","turkish":"kelime"}, ...]',
                      alignLabelWithHint: true,
                    ),
                    maxLines: 10,
                    minLines: 5,
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: _isImporting ? null : _importJson,
                      icon: _isImporting
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child:
                                  CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.upload),
                      label: Text(
                          _isImporting ? 'Yukleniyor...' : 'Import Et'),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Card(
            color: Colors.blue[50],
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.info_outline, color: Colors.blue[700]),
                      const SizedBox(width: 8),
                      Text(
                        'JSON Formati',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Colors.blue[700],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.grey[100],
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Text(
                      '[\n'
                      '  {"english": "abundant", "turkish": "bol"},\n'
                      '  {"english": "chronic", "turkish": "kronik"},\n'
                      '  {"english": "symptom", "turkish": "belirti"}\n'
                      ']',
                      style: TextStyle(
                        fontFamily: 'monospace',
                        fontSize: 13,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _importJson() {
    if (_setNameController.text.isEmpty || _jsonController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Set adi ve JSON verisi gerekli.')),
      );
      return;
    }

    setState(() => _isImporting = true);

    // TODO: Call bulk import API
    Future.delayed(const Duration(seconds: 2), () {
      setState(() => _isImporting = false);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Import basarili!')),
      );
      _setNameController.clear();
      _jsonController.clear();
    });
  }
}
