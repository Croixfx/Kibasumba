/// Date helpers shared by the pregnancy form and dashboard.
library;

String formatDdMmYyyy(DateTime date) {
  final dd = date.day.toString().padLeft(2, '0');
  final mm = date.month.toString().padLeft(2, '0');
  return '$dd/$mm/${date.year}';
}

/// Mirror of the backend's EDD calculation (Naegele's rule) so the form can
/// preview the EDD live. The backend value is still authoritative.
DateTime calculateEdd(DateTime lmp) {
  final base = lmp.add(const Duration(days: 7));
  int month;
  int year;
  if (base.month <= 3) {
    month = base.month + 9;
    year = base.year;
  } else {
    month = base.month - 3;
    year = base.year + 1;
  }
  // Clamp the day for shorter target months.
  final lastDay = DateTime(year, month + 1, 0).day;
  return DateTime(year, month, base.day <= lastDay ? base.day : lastDay);
}

int weeksSince(DateTime date) => DateTime.now().difference(date).inDays ~/ 7;

/// Today minus [months] calendar months, day clamped to the target month.
DateTime monthsAgo(int months) {
  final now = DateTime.now();
  int month = now.month - months;
  int year = now.year;
  while (month < 1) {
    month += 12;
    year -= 1;
  }
  final lastDay = DateTime(year, month + 1, 0).day;
  return DateTime(year, month, now.day <= lastDay ? now.day : lastDay);
}
