using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Utilities
{
	public abstract class Singleton<T> where T: class
    {
        private static readonly Lazy<T> lazy = new Lazy<T>( () => (T)Activator.CreateInstance(typeof(T), true) );

        public static T Get { get { return lazy.Value; } }

        protected Singleton()
        {
        }
    }
}