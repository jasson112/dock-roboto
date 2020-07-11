<?php
/**
 * The base configuration for WordPress
 *
 * The wp-config.php creation script uses this file during the
 * installation. You don't have to use the web site, you can
 * copy this file to "wp-config.php" and fill in the values.
 *
 * This file contains the following configurations:
 *
 * * MySQL settings
 * * Secret keys
 * * Database table prefix
 * * ABSPATH
 *
 * @link https://codex.wordpress.org/Editing_wp-config.php
 *
 * @package WordPress
 */


define('WP_HOME','http://devcwcbusiness.com');
define('WP_SITEURL','http://devcwcbusiness.com');

// ** MySQL settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define('DB_NAME', 'cwcbusin_wp');

/** MySQL database username */
define('DB_USER', 'root');

/** MySQL database password */
define('DB_PASSWORD', 'root');

/** MySQL hostname */
define('DB_HOST', 'cw-mysql');

/** Database Charset to use in creating database tables. */
define('DB_CHARSET', 'utf8');

/** The Database Collate type. Don't change this if in doubt. */
define('DB_COLLATE', '');

/**#@+
 * Authentication Unique Keys and Salts.
 *
 * Change these to different unique phrases!
 * You can generate these using the {@link https://api.wordpress.org/secret-key/1.1/salt/ WordPress.org secret-key service}
 * You can change these at any point in time to invalidate all existing cookies. This will force all users to have to log in again.
 *
 * @since 2.6.0
 */
define('AUTH_KEY',         'Xq(CQ`>9ds>q0uh;F<Lna|[n)$L@eNpz{`yy(Qq6aK|Yi4W+Uhca>u ]A{aG;2BW');
define('SECURE_AUTH_KEY',  '@xce9lBH1_VTlFNqNh$`L$%en(3:s9olp+]-N;;mKC2rNb$fVB!:yNd:Grdk;zi-');
define('LOGGED_IN_KEY',    'R,(S!E_s3C@SPR[ZIwS4c6h!sV7HhE[-}-b+q_$P>-9$X6K c)dLPKbR9T7!if:r');
define('NONCE_KEY',        'q[|=dCQ*Z{r+Z,[lq^VYMwXA#/Y|#qxB}(KH?:]M2!l*:~!l6+{HWuYkleQCzGNr');
define('AUTH_SALT',        '4N6Yk.h>bezsDO!B)HE&TYF9Od&HWLyMM>5|UYP<)zi@3Nx}zCg=WJ70bGy?+=o]');
define('SECURE_AUTH_SALT', '++DE)c9])R-;mY;XSPx-lc.@wa0yqm8Hn-&(.e+Es .R55/!]/ OMs.76T(cN*Ws');
define('LOGGED_IN_SALT',   'jGjui1_jf!zJi=UM-ImZA7ZKc.Ud5 L~|oi,@02y9U ;d@-cM<^YUZN|FT[}K4_[');
define('NONCE_SALT',       '#[T[(pcq-/$7UGkW@}3RyrtqZ@[#:Ba169*H%t+%!1F7TMW}hUPwD;F]W{oL-TnR');

/**#@-*/

/**
 * WordPress Database Table prefix.
 *
 * You can have multiple installations in one database if you give each
 * a unique prefix. Only numbers, letters, and underscores please!
 */
$table_prefix  = 'wp_';

/**
 * For developers: WordPress debugging mode.
 *
 * Change this to true to enable the display of notices during development.
 * It is strongly recommended that plugin and theme developers use WP_DEBUG
 * in their development environments.
 *
 * For information on other constants that can be used for debugging,
 * visit the Codex.
 *
 * @link https://codex.wordpress.org/Debugging_in_WordPress
 */
define('WP_DEBUG', true);
define( 'WP_DEBUG_LOG', true );
define( 'WP_DEBUG_DISPLAY', false );
define('WP_CACHE', false);

/* That's all, stop editing! Happy blogging. */

/** Absolute path to the WordPress directory. */
if ( !defined('ABSPATH') )
    define('ABSPATH', dirname(__FILE__) . '/');

/** Sets up WordPress vars and included files. */
require_once(ABSPATH . 'wp-settings.php');