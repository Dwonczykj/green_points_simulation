// **************************************************************************
// AutoRouteGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND

// **************************************************************************
// AutoRouteGenerator
// **************************************************************************
//
// ignore_for_file: type=lint

import 'package:auto_route/auto_route.dart' as _i2;
import 'package:flutter/material.dart' as _i4;

import '../ui/screens/debug_screen.dart' as _i3;
import '../ui/screens/screens.dart' as _i1;

class AppRouter extends _i2.RootStackRouter {
  AppRouter([_i4.GlobalKey<_i4.NavigatorState>? navigatorKey])
      : super(navigatorKey);

  @override
  final Map<String, _i2.PageFactory> pagesMap = {
    NavigationRailSelectedViewRoute.name: (routeData) {
      return _i2.MaterialPageX<dynamic>(
          routeData: routeData,
          child: const _i1.NavigationRailSelectedViewPage());
    },
    CustomerViewRouter.name: (routeData) {
      return _i2.MaterialPageX<dynamic>(
          routeData: routeData, child: const _i2.EmptyRouterPage());
    },
    ViewSimulationRouter.name: (routeData) {
      return _i2.MaterialPageX<dynamic>(
          routeData: routeData, child: const _i2.EmptyRouterPage());
    },
    DebugRouter.name: (routeData) {
      return _i2.MaterialPageX<dynamic>(
          routeData: routeData, child: const _i2.EmptyRouterPage());
    },
    CustomerViewScreenRoute.name: (routeData) {
      return _i2.MaterialPageX<dynamic>(
          routeData: routeData, child: const _i1.CustomerViewScreenPage());
    },
    ViewSimulationRoute.name: (routeData) {
      return _i2.MaterialPageX<dynamic>(
          routeData: routeData, child: const _i1.ViewSimulationPage());
    },
    DebugRoute.name: (routeData) {
      return _i2.MaterialPageX<dynamic>(
          routeData: routeData, child: const _i3.DebugPage());
    }
  };

  @override
  List<_i2.RouteConfig> get routes => [
        _i2.RouteConfig(NavigationRailSelectedViewRoute.name,
            path: '/',
            children: [
              _i2.RouteConfig(CustomerViewRouter.name,
                  path: 'view',
                  parent: NavigationRailSelectedViewRoute.name,
                  children: [
                    _i2.RouteConfig(CustomerViewScreenRoute.name,
                        path: '', parent: CustomerViewRouter.name),
                    _i2.RouteConfig('*#redirect',
                        path: '*',
                        parent: CustomerViewRouter.name,
                        redirectTo: '',
                        fullMatch: true)
                  ]),
              _i2.RouteConfig(ViewSimulationRouter.name,
                  path: 'sim',
                  parent: NavigationRailSelectedViewRoute.name,
                  children: [
                    _i2.RouteConfig(ViewSimulationRoute.name,
                        path: '', parent: ViewSimulationRouter.name),
                    _i2.RouteConfig('*#redirect',
                        path: '*',
                        parent: ViewSimulationRouter.name,
                        redirectTo: '',
                        fullMatch: true)
                  ]),
              _i2.RouteConfig(DebugRouter.name,
                  path: 'debug',
                  parent: NavigationRailSelectedViewRoute.name,
                  children: [
                    _i2.RouteConfig(DebugRoute.name,
                        path: '', parent: DebugRouter.name),
                    _i2.RouteConfig('*#redirect',
                        path: '*',
                        parent: DebugRouter.name,
                        redirectTo: '',
                        fullMatch: true)
                  ])
            ])
      ];
}

/// generated route for
/// [_i1.NavigationRailSelectedViewPage]
class NavigationRailSelectedViewRoute extends _i2.PageRouteInfo<void> {
  const NavigationRailSelectedViewRoute({List<_i2.PageRouteInfo>? children})
      : super(NavigationRailSelectedViewRoute.name,
            path: '/', initialChildren: children);

  static const String name = 'NavigationRailSelectedViewRoute';
}

/// generated route for
/// [_i2.EmptyRouterPage]
class CustomerViewRouter extends _i2.PageRouteInfo<void> {
  const CustomerViewRouter({List<_i2.PageRouteInfo>? children})
      : super(CustomerViewRouter.name, path: 'view', initialChildren: children);

  static const String name = 'CustomerViewRouter';
}

/// generated route for
/// [_i2.EmptyRouterPage]
class ViewSimulationRouter extends _i2.PageRouteInfo<void> {
  const ViewSimulationRouter({List<_i2.PageRouteInfo>? children})
      : super(ViewSimulationRouter.name,
            path: 'sim', initialChildren: children);

  static const String name = 'ViewSimulationRouter';
}

/// generated route for
/// [_i2.EmptyRouterPage]
class DebugRouter extends _i2.PageRouteInfo<void> {
  const DebugRouter({List<_i2.PageRouteInfo>? children})
      : super(DebugRouter.name, path: 'debug', initialChildren: children);

  static const String name = 'DebugRouter';
}

/// generated route for
/// [_i1.CustomerViewScreenPage]
class CustomerViewScreenRoute extends _i2.PageRouteInfo<void> {
  const CustomerViewScreenRoute()
      : super(CustomerViewScreenRoute.name, path: '');

  static const String name = 'CustomerViewScreenRoute';
}

/// generated route for
/// [_i1.ViewSimulationPage]
class ViewSimulationRoute extends _i2.PageRouteInfo<void> {
  const ViewSimulationRoute() : super(ViewSimulationRoute.name, path: '');

  static const String name = 'ViewSimulationRoute';
}

/// generated route for
/// [_i3.DebugPage]
class DebugRoute extends _i2.PageRouteInfo<void> {
  const DebugRoute() : super(DebugRoute.name, path: '');

  static const String name = 'DebugRoute';
}
