// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

UserModel _$UserModelFromJson(Map<String, dynamic> json) => UserModel(
      id: json['id'] as String,
      email: json['email'] as String,
      fullName: json['full_name'] as String,
      role: json['role'] as String,
      institutionId: json['institution_id'] as String?,
      createdAt: json['created_at'] as String,
      lastLogin: json['last_login'] as String?,
      isActive: json['is_active'] as bool,
    );

Map<String, dynamic> _$UserModelToJson(UserModel instance) =>
    <String, dynamic>{
      'id': instance.id,
      'email': instance.email,
      'full_name': instance.fullName,
      'role': instance.role,
      'institution_id': instance.institutionId,
      'created_at': instance.createdAt,
      'last_login': instance.lastLogin,
      'is_active': instance.isActive,
    };
