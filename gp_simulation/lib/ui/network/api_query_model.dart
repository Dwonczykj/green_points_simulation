class AAPIQuery {
  factory AAPIQuery.fromJson(Map<String, dynamic> json) => AAPIQuery(
        query: json['q'] as String,
      );

  Map<String, dynamic> toJson() => <String, dynamic>{
        'q': query,
      };

  String query;

  AAPIQuery({required this.query});
}
