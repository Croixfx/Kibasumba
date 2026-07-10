import 'package:flutter_test/flutter_test.dart';

import 'package:kibasumba/main.dart';

void main() {
  testWidgets('App starts and shows the phone entry field', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KibasumbaApp());
    await tester.pumpAndSettle();

    expect(find.text('Numero ya telefoni'), findsOneWidget);
    expect(find.text('Komeza'), findsOneWidget);
  });
}
