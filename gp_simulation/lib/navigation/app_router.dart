/// auto_route docs: -> https://autoroute.vercel.app/introduction, https://www.notion.so/gember/Dart-Flutter-Cheat-Sheet-33f53ff62f334411ab02640c3b931bd8#593631677e4d4358a0c37c0f9f40bded
import 'package:auto_route/auto_route.dart';

import '../ui/screens/screens.dart';



// @CupertinoAutoRouter
// @AdaptiveAutoRouter
// @CustomAutoRouter
@MaterialAutoRouter(
  replaceInRouteName: 'Page,Route',
  routes: <AutoRoute>[
    // AutoRoute(page: CustomerViewScreenPage, initial: true),
    // AutoRoute(page: ViewSimulationPage),
    AutoRoute(
      path: "/",
      // page: MyHomePage,
      page: NavigationRailSelectedViewPage,
      children: [
        // our BooksRouter has been moved into the children field
        AutoRoute(
          path: "view",
          name: "CustomerViewRouter",
          page: EmptyRouterPage,
          children: [
            AutoRoute(path: '', page: CustomerViewScreenPage),
            // AutoRoute(path: ':bookId', page: BookDetailsPage),
            RedirectRoute(path: '*', redirectTo: ''),
          ],
        ),
        // our AccountRouter has been moved into the children field
        AutoRoute(
          path: "sim",
          name: "ViewSimulationRouter",
          page: EmptyRouterPage,
          children: [
            AutoRoute(path: '', page: ViewSimulationPage),
            // AutoRoute(path: 'details', page: AccountDetailsPage),
            RedirectRoute(path: '*', redirectTo: ''),
          ],
        ),
      ],
    ),
  ],
)
class $AppRouter {}
