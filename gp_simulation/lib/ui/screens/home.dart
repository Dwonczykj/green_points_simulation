import 'package:auto_route/auto_route.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:webtemplate/ui/screens/dummy_screen.dart';
import 'package:webtemplate/ui/screens/i_page_wrapper.dart';
import 'package:webtemplate/ui/screens/view_simulation.dart';
import '../../navigation/app_router.gr.dart';
import '../model/models.dart';
import '../network/network.dart';
import 'customer_view_screen.dart';
// import 'package:webtemplate/ui/components/retailer_consumer_spider.dart';

class MyHomePage extends StatefulWidget {
  const MyHomePage({Key? key}) : super(key: key);

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  
  @override
  Widget build(BuildContext context) {
    // return const ViewSimulationPage();
    return AutoTabsScaffold(
      routes: const [
        CustomerViewRouter(),
        ViewSimulationRouter(),
      ],
      bottomNavigationBuilder: (_, tabsRouter) {
        return BottomNavigationBar(
          currentIndex: tabsRouter.activeIndex,
          onTap: tabsRouter.setActiveIndex,
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.book),
              label: 'Books',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.account_box),
              label: 'Account',
            ),
          ],
        );
      },
    );
  }
}

class NavigationRailSelectedViewPage extends StatefulWidget {
  const NavigationRailSelectedViewPage({Key? key}) : super(key: key);

  @override
  State<NavigationRailSelectedViewPage> createState() =>
      _NavigationRailSelectedViewPageState();
}

class _NavigationRailSelectedViewPageState
    extends State<NavigationRailSelectedViewPage> {
  int _selectedIndex = 1;
  final routes = const <PageRouteInfo<void>>[
    CustomerViewRouter(),
    ViewSimulationRouter(),
  ];
  final routeTitles = <String>[
    ViewSimulationPage.title,
    CustomerViewScreenPage.title,
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
              icon: Icon(Icons.person),
              label: 'Visualise',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.data_exploration),
              label: 'Simulate',
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
