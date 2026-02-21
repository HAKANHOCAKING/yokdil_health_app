import 'package:json_annotation/json_annotation.dart';
import '../../domain/entities/user.dart';

part 'user_model.g.dart';

@JsonSerializable()
class UserModel {
  final String id;
  final String email;
  @JsonKey(name: 'full_name')
  final String fullName;
  final String role;
  @JsonKey(name: 'institution_id')
  final String? institutionId;
  @JsonKey(name: 'created_at')
  final String createdAt;
  @JsonKey(name: 'last_login')
  final String? lastLogin;
  @JsonKey(name: 'is_active')
  final bool isActive;

  UserModel({
    required this.id,
    required this.email,
    required this.fullName,
    required this.role,
    this.institutionId,
    required this.createdAt,
    this.lastLogin,
    required this.isActive,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) => _$UserModelFromJson(json);
  Map<String, dynamic> toJson() => _$UserModelToJson(this);

  User toEntity() {
    return User(
      id: id,
      email: email,
      fullName: fullName,
      role: role,
      institutionId: institutionId,
      createdAt: DateTime.parse(createdAt),
      lastLogin: lastLogin != null ? DateTime.parse(lastLogin!) : null,
      isActive: isActive,
    );
  }
}
