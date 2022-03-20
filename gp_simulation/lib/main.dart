import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:webtemplate/ui/model/models.dart';
import 'package:webtemplate/ui/style/app_theme.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:logging/logging.dart';

import 'navigation/app_router.gr.dart';
import 'ui/model/all_models.dart';
import 'ui/network/network.dart';
import 'ui/screens/screens.dart';

Future main() async {
  _setupLogging();
  WidgetsFlutterBinding.ensureInitialized();
  await dotenv.load(fileName: '.env');
  runApp(MyApp());
}

void _setupLogging() {
  Logger.root.level = Level.INFO;
  Logger.root.onRecord.listen(
    (rec) {
      print('${rec.level.name}: ${rec.time}: ${rec.message}');
    },
  );
}

class MyApp extends StatelessWidget {
  MyApp({Key? key}) : super(key: key);

  final _appRouter = AppRouter();

  final IMarketStateViewer _marketStateViewer =
      MarketStateViewerFactory.create(false).realInstance!;

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        // State Managers
        ChangeNotifierProvider<IMarketStateViewer>(
          create: (context) => _marketStateViewer,
          lazy: false,
        ),
        ChangeNotifierProvider<AppStateManager>(
          create: (context) =>
              AppStateManager.getInstance(_marketStateViewer),
          lazy: false,
        ),

        //Services
        // Provider<ServiceInterface<CustomerModel>>(
        //   create: (_) => MockService.create(),
        //   lazy: false,
        // ),
      ],
      child: MaterialApp.router(
        routerDelegate: _appRouter.delegate(),
        routeInformationParser: _appRouter.defaultRouteParser(),
        title: 'Gember Conscientious Points Simulation',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.dark(),
        backButtonDispatcher:
            RootBackButtonDispatcher(), //For handling Androids natibve back button
      ),
    );
  }
}
