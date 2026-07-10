// Hardcoded Rwanda administrative and health-facility data for the MVP.
//
// TODO: replace with live MINISANTE API data when integration is approved.
// This file is deliberately the ONLY place location data lives, so the
// handover is a matter of swapping these constants for API calls.

const List<String> rwandaProvinces = [
  'Kigali City',
  'Northern',
  'Southern',
  'Eastern',
  'Western',
];

/// All 30 districts of Rwanda, grouped by province.
const Map<String, List<String>> rwandaDistrictsByProvince = {
  'Kigali City': ['Gasabo', 'Kicukiro', 'Nyarugenge'],
  'Northern': ['Burera', 'Gakenke', 'Gicumbi', 'Musanze', 'Rulindo'],
  'Southern': [
    'Gisagara',
    'Huye',
    'Kamonyi',
    'Muhanga',
    'Nyamagabe',
    'Nyanza',
    'Nyaruguru',
    'Ruhango',
  ],
  'Eastern': [
    'Bugesera',
    'Gatsibo',
    'Kayonza',
    'Kirehe',
    'Ngoma',
    'Nyagatare',
    'Rwamagana',
  ],
  'Western': [
    'Karongi',
    'Ngororero',
    'Nyabihu',
    'Nyamasheke',
    'Rubavu',
    'Rusizi',
    'Rutsiro',
  ],
};

/// Major public hospitals / referral facilities per district.
///
/// TODO: replace with live MINISANTE API data when integration is approved.
/// Real facility names are used where known; the district hospital name is
/// the fallback.
const Map<String, List<String>> rwandaHospitalsByDistrict = {
  // Kigali City
  'Gasabo': [
    'King Faisal Hospital',
    'Kibagabaga District Hospital',
    'Kacyiru District Hospital',
  ],
  'Kicukiro': [
    'Rwanda Military Hospital (Kanombe)',
    'Masaka District Hospital',
  ],
  'Nyarugenge': [
    'CHUK (Centre Hospitalier Universitaire de Kigali)',
    'Muhima District Hospital',
  ],
  // Northern
  'Burera': ['Butaro District Hospital'],
  'Gakenke': ['Ruli District Hospital', 'Nemba District Hospital'],
  'Gicumbi': ['Byumba District Hospital'],
  'Musanze': ['Ruhengeri Referral Hospital'],
  'Rulindo': ['Rutongo District Hospital', 'Kinihira Provincial Hospital'],
  // Southern
  'Gisagara': ['Kibilizi District Hospital', 'Gakoma District Hospital'],
  'Huye': [
    'CHUB (Butare University Teaching Hospital)',
    'Kabutare District Hospital',
  ],
  'Kamonyi': ['Remera-Rukoma District Hospital', 'Nyamiyaga Health Centre'],
  'Muhanga': ['Kabgayi District Hospital'],
  'Nyamagabe': ['Kigeme District Hospital', 'Kaduha District Hospital'],
  'Nyanza': ['Nyanza District Hospital'],
  'Nyaruguru': ['Munini District Hospital', 'Kibeho District Hospital'],
  'Ruhango': ['Ruhango Provincial Hospital', 'Gitwe District Hospital'],
  // Eastern
  'Bugesera': ['Nyamata District Hospital'],
  'Gatsibo': ['Ngarama District Hospital', 'Kiziguro District Hospital'],
  'Kayonza': ['Gahini District Hospital', 'Rwinkwavu District Hospital'],
  'Kirehe': ['Kirehe District Hospital'],
  'Ngoma': ['Kibungo Referral Hospital'],
  'Nyagatare': ['Nyagatare District Hospital'],
  'Rwamagana': ['Rwamagana Provincial Hospital'],
  // Western
  'Karongi': ['Kibuye Referral Hospital', 'Kirinda District Hospital'],
  'Ngororero': ['Kabaya District Hospital', 'Muhororo District Hospital'],
  'Nyabihu': ['Shyira District Hospital'],
  'Nyamasheke': ['Bushenge Provincial Hospital', 'Kibogora District Hospital'],
  'Rubavu': ['Gisenyi District Hospital'],
  'Rusizi': ['Gihundwe District Hospital', 'Mibilizi District Hospital'],
  'Rutsiro': ['Murunda District Hospital'],
};
