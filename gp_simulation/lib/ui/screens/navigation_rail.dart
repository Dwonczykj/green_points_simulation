import 'package:auto_route/auto_route.dart';
import 'package:flutter/material.dart';

import 'package:webtemplate/ui/screens/view_simulation.dart';
import '../../navigation/app_router.gr.dart';

import 'customer_view_screen.dart';
import 'debug_screen.dart';

class NavigationRailSelectedViewPage extends StatefulWidget {
  const NavigationRailSelectedViewPage({Key? key}) : super(key: key);

  @override
  State<NavigationRailSelectedViewPage> createState() =>
      _NavigationRailSelectedViewPageState();
}

class _NavigationRailSelectedViewPageState
    extends State<NavigationRailSelectedViewPage> {
  int _selectedIndex = 1;
  final RouteObserver<PageRoute> routeObserver = RouteObserver<PageRoute>();
  final routes = const <PageRouteInfo<void>>[
    ViewSimulationRouter(),
    CustomerViewRouter(),
    DebugRouter(),
  ];
  final routeTitles = <String>[
    ViewSimulationPage.title,
    CustomerViewScreenPage.title,
    DebugPage.title,
  ];

  @override
  Widget build(BuildContext context) {
    return AutoTabsScaffold(
      routes: routes,
      bottomNavigationBuilder: (_, tabsRouter) {
        return BottomNavigationBar(
          currentIndex: tabsRouter.activeIndex,
          onTap: tabsRouter.setActiveIndex,
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.data_exploration),
              label: 'Simulate',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.person),
              label: 'Visualise',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.construction),
              label: 'Debug',
            ),
          ],
        );
      },
      // builder: (context, selectedWidget, animationChangeSelectedWidget) {
      //   return Scaffold(
      //     appBar: AppBar(
      //       backgroundColor: Theme.of(context).bottomAppBarColor,
      //       title: Text(routeTitles[_selectedIndex]),
      //     ),
      //     body: SafeArea(
      //       child: Row(
      //         children: <Widget>[
      //           NavigationRail(
      //             selectedIndex: _selectedIndex,
      //             onDestinationSelected: (int index) {
      //               setState(() {
      //                 _selectedIndex = index;
      //               });
      //               // var router = AutoRouter.of(context);
      //               // if (index == 1) {
      //               //   router.navigate(BooksRoute());
      //               // } else if (index == 2) {
      //               // } else if (index == 3) {
      //               // } else {}
      //             },
      //             labelType: NavigationRailLabelType.selected,
      //             destinations: const <NavigationRailDestination>[
      //               NavigationRailDestination(
      //                 icon: Icon(Icons.favorite_border),
      //                 selectedIcon: Icon(Icons.favorite),
      //                 label: Text('First'),
      //               ),
      //               NavigationRailDestination(
      //                 icon: Icon(Icons.bookmark_border),
      //                 selectedIcon: Icon(Icons.book),
      //                 label: Text('Second'),
      //               ),
      //               NavigationRailDestination(
      //                 icon: Icon(Icons.star_border),
      //                 selectedIcon: Icon(Icons.star),
      //                 label: Text('Third'),
      //               ),
      //             ],
      //           ),
      //           const VerticalDivider(thickness: 1, width: 1),
      //           // This is the main content.
      //           Expanded(
      //             /*TODO: Inject MarketStateService where BlocProvided create is in example:
      //                         https://autoroute.vercel.app/basics/wrapping_routes and then each autoroute
      //                         should be wrapped with the scaffold using ipagewrapper which ipagewrapper
      //                         expects the marketstatedependency. then Display tyhe navigation rail here
      //                         where the selectedRoute is our scaffold wrapped page route with the dependency injection.*/

      //             child: selectedWidget,
      //             // child: widget.childGetter(marketStateService, snapshot),
      //           ),
      //         ],
      //       ),
      //     ),
      //   );
      // }
    );
  }
}
