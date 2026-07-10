/// The active pregnancy as returned by the backend.
class Pregnancy {
  final int id;
  final String fullName;
  final int age;
  final int gravida;
  final int parity;
  final DateTime lmpDate;
  final bool isLmpEstimated;
  final DateTime eddDate;
  final String province;
  final String district;
  final String hospital;
  final String healthCentre;
  final String healthPost;
  final int currentWeek;

  const Pregnancy({
    required this.id,
    required this.fullName,
    required this.age,
    required this.gravida,
    required this.parity,
    required this.lmpDate,
    required this.isLmpEstimated,
    required this.eddDate,
    required this.province,
    required this.district,
    required this.hospital,
    required this.healthCentre,
    required this.healthPost,
    required this.currentWeek,
  });

  factory Pregnancy.fromJson(Map<String, dynamic> json) {
    return Pregnancy(
      id: json['id'] as int,
      fullName: json['full_name'] as String,
      age: json['age'] as int,
      gravida: json['gravida'] as int,
      parity: json['parity'] as int,
      lmpDate: DateTime.parse(json['lmp_date'] as String),
      isLmpEstimated: json['is_lmp_estimated'] as bool,
      eddDate: DateTime.parse(json['edd_date'] as String),
      province: (json['province'] ?? '') as String,
      district: (json['district'] ?? '') as String,
      hospital: (json['hospital'] ?? '') as String,
      healthCentre: (json['health_centre'] ?? '') as String,
      healthPost: (json['health_post'] ?? '') as String,
      currentWeek: json['current_week'] as int,
    );
  }
}
