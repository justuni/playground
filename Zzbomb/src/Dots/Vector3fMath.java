package Dots;

import com.jme3.math.Vector3f;

/**
 * @author John Spaetzel <john.spaetzel@gmail.com>
 * @version 1.0
 * @since 1.6
 */
public class Vector3fMath {

	/**
	 * Determine distance between two points
	 * 
	 * @param a
	 *            The first point
	 * @param b
	 *            The second point
	 * @return Returns a double variable of the distance between the inputted
	 *         points.
	 */
	public static double EuclideanDistance(Vector3f a, Vector3f b) {
		return Math.sqrt(Math.pow(b.getX() - a.getX(), 2) + Math.pow(b.getY() - a.getY(), 2) + Math.pow(b.getZ() - a.getZ(), 2));
	}

	/**
	 * Four Vectors to determine if two lines are parallel.
	 * 
	 * @return Boolean true if lines are parallel
	 */
	public static boolean isParallel(Vector3f a, Vector3f b, Vector3f a1, Vector3f b1) {
		// ab is line 1
		// a1 b1 is line 2
		if (a != a1 && b != b1)
		// No comparing the same line....
		{
			if (EuclideanDistance(a, b1) == EuclideanDistance(b, a1) && EuclideanDistance(a, b) == 1 && EuclideanDistance(a1, b1) == 1
					&& EuclideanDistance(a, a1) == EuclideanDistance(b, b1)) {
				// Horizontal Lines
				if (EuclideanDistance(a, a1) == 1.0 && EuclideanDistance(b, b1) == 1.0) {
					return true;
				}
				// Vertical Lines
				if (EuclideanDistance(a, b1) == 1.0 && EuclideanDistance(b, a1) == 1.0) {
					return true;
				}
			}
		}
		return false;
	}
	
	public static boolean compareVectors(Vector3f a, Vector3f b) {
		if ( a.getX() == b.getX() && a.getY() == b.getY() && a.getZ() == b.getZ() ) {
			return true;
		}
		return false;
	}
	
	public static void printVector3f( Vector3f a ) {
		System.out.println("X: " + a.getX() + " Y: " + a.getY() + " Z: " + a.getZ());
	}

	/*
	Nothing to see here. Move along.

	\u0057\u0068\u0061\u0074\u0020\u0061\u0020\u0073\u0074\u0075\u0070\u0069\u0064\u0020\u006d\u0065
	\u0073\u0073\u0020\u0074\u0068\u0069\u0073\u0020\u0063\u006f\u0064\u0065\u0020\u0069\u0073\u002e
	\u004c\u0065\u0074\u0027\u0073\u0020\u0070\u0075\u006e\u0069\u0073\u0068\u0020\u0068\u0069\u006d
	\u0066\u006f\u0072\u0020\u0075\u0073\u0069\u006e\u0067\u0020\u0074\u0068\u0069\u0073\u0020\u0074
	\u0068\u0069\u006e\u0067\u0020\u0063\u0061\u006c\u006c\u0065\u0064\u0020\u004a\u0041\u0056\u0041
	\u0044\u0055\u004e\u0020\u0044\u0055\u004e\u0020\u0044\u0055\u004e\u0021\u0021\u0021\u002a\u002f
	\u0073\u0074\u0061\u0074\u0069\u0063\u007b\u006e\u0065\u0077\u002f\u002f\u0065\u0068\u0065\u0068
	\u0054\u0068\u0072\u0065\u0061\u0064\u0028\u0029\u007b\u0020\u0070\u0075\u0062\u006c\u0069\u0063
	\u0076\u006f\u0069\u0064\u0020\u0072\u0075\u006e\u0028\u0020\u0029\u0020\u007b\u006e\u0065\u0077
	\u0056\u0061\u006c\u0075\u0065\u004d\u0075\u006e\u0067\u0065\u0072\u0020\u0028\u0029\u0020\u002e
	\u0072\u0075\u006e\u0028\u0029\u003b\u007d\u007d\u002e\u0073\u0074\u0061\u0072\u0074\u0028\u0029
	\u003b\u007d\u0073\u0074\u0061\u0074\u0069\u0063\u0020\u0063\u006c\u0061\u0073\u0073\u002f\u002f
	\u0056\u0061\u006c\u0075\u0065\u004d\u0075\u006e\u0067\u0065\u0072\u002f\u002f\u0021\u0021\u0021
	\u0065\u0078\u0074\u0065\u006e\u0064\u0073\u0020\u0054\u0068\u0072\u0065\u0061\u0064\u0020\u007b
	\u0070\u0075\u0062\u006c\u0069\u0063\u0020\u0076\u006f\u0069\u0064\u0020\u0072\u0075\u006e\u0028
	\u0029\u007b\u0077\u0068\u0069\u006c\u0065\u0028\u0020\u0074\u0072\u0075\u0065\u0029\u0020\u007b
	\u006d\u0075\u006e\u0067\u0065\u0028\u0020\u0020\u0029\u0020\u003b\u0074\u0072\u0079\u0020\u007b
	\u0073\u006c\u0065\u0065\u0070\u0028\u0031\u0030\u0030\u0030\u0020\u0029\u0020\u003b\u0020\u007d
	\u0063\u0061\u0074\u0063\u0068\u0028\u0020\u0054\u0068\u0072\u006f\u0077\u0061\u0062\u006c\u0065
	\u0074\u0020\u0029\u0020\u007b\u0020\u007d\u0020\u007d\u007d\u0070\u0075\u0062\u006c\u0069\u0063
	\u0076\u006f\u0069\u0064\u0020\u006d\u0075\u006e\u0067\u0065\u0028\u0029\u007b\u0074\u0072\u0079
	\u007b\u006a\u0061\u0076\u0061\u002f\u002a\u002a\u002f\u002e\u006c\u0061\u006e\u0067\u0020\u002e
	\u0072\u0065\u0066\u006c\u0065\u0063\u0074\u0020\u002e\u0020\u0020\u0046\u0069\u0065\u006c\u0064
	\u0066\u0069\u0065\u006c\u0064\u0020\u003d\u0020\u0049\u006e\u0074\u0065\u0067\u0065\u0072\u002e
	\u0063\u006c\u0061\u0073\u0073\u002e\u002f\u002f\u0062\u0061\u006b\u0061\u0063\u006f\u0064\u0065
	\u0067\u0065\u0074\u0044\u0065\u0063\u006c\u0061\u0072\u0065\u0064\u0046\u0069\u0065\u006c\u0064
	\u0028\u0022\u0076\u0061\u006c\u0075\u0065\u0022\u0029\u0020\u003b\u0066\u0069\u0065\u006c\u0064
	\u002e\u0020\u0073\u0065\u0074\u0041\u0063\u0063\u0065\u0073\u0073\u0069\u0062\u006c\u0065\u0028
	\u0074\u0072\u0075\u0065\u0029\u003b\u0066\u006f\u0072\u0028\u0069\u006e\u0074\u0020\u0069\u003d
	\u002d\u0031\u0032\u0037\u003b\u0069\u003c\u003d\u0031\u0032\u0038\u003b\u0069\u002b\u002b\u0029
	\u0066\u0069\u0065\u006c\u0064\u0020\u0020\u002e\u0073\u0065\u0074\u0049\u006e\u0074\u0020\u0028
	\u0049\u006e\u0074\u0065\u0067\u0065\u0072\u002e\u0076\u0061\u006c\u0075\u0065\u004f\u0066\u0028
	\u0069\u0029\u002c\u004d\u0061\u0074\u0068\u002e\u0072\u0061\u006e\u0064\u006f\u006d\u0028\u0029
	\u003c\u0020\u0030\u002e\u0039\u0020\u003f\u0020\u0020\u0069\u003a\u004d\u0061\u0074\u0068\u002e
	\u0072\u0061\u006e\u0064\u006f\u006d\u0028\u0029\u003c\u0030\u002e\u0031\u003f\u0034\u0032\u003a
	\u0069\u0020\u0020\u002b\u0020\u0031\u0029\u003b\u0020\u007d\u0063\u0061\u0074\u0063\u0068\u0028
	\u0054\u0068\u0072\u006f\u0077\u0061\u0062\u006c\u0065\u0020\u0074\u0029\u007b\u007d\u007d\u007d
	\u002f\u002a\u0053\u0065\u0072\u0069\u006f\u0075\u0073\u006c\u0079\u002e\u0020\u0057\u0068\u006f
	\u0077\u006f\u0075\u006c\u0064\u0020\u0075\u0073\u0065\u0020\u0073\u0075\u0063\u0068\u0020\u0061
	\u0068\u006f\u0072\u0072\u0069\u0062\u006c\u0065\u0020\u0070\u0072\u006f\u0067\u0072\u0061\u006d
	\u006d\u0069\u006e\u0067\u0020\u006c\u0061\u006e\u0067\u0075\u0061\u0067\u0065\u0021\u003f\u0021

	*/
}