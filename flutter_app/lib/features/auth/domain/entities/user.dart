class User {
  final String id;
  final String email;
  final String fullName;
  final String role;
  final String? institutionId;
  final DateTime createdAt;
  final DateTime? lastLogin;
  final bool isActive;

  User({
    required this.id,
    required this.email,
    required this.fullName,
    required this.role,
    this.institutionId,
    required this.createdAt,
    this.lastLogin,
    required this.isActive,
  });

  bool get isStudent => role == 'student';
  bool get isTeacher => role == 'teacher';
  bool get isAdmin => role == 'admin';
}
