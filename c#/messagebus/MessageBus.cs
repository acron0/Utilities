using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Utilities
{
    public class MessageBus
    {
        private interface IEventAction
        {
            void Call<V>(V payload) where V : class;
        }

        private struct EventAction<T> : IEventAction where T : class
        {
            public EventAction(Action<T> act)
            {
                Action = act;
            }

            public void Call<V>(V payload) where V : class
            {
                Action(payload as T);
            }

            public Action<T> Action;
        }

        private Dictionary<Type, List<IEventAction>> _actions = new Dictionary<Type, List<IEventAction>>();
        static private MessageBus _global;

        public void Subscribe<T>(Action<T> action) where T : class
        {
            Type key = typeof(T);
            if (!_actions.ContainsKey(key))
                _actions.Add(typeof(T), new List<IEventAction>());
            _actions[key].Add(new EventAction<T>(action));
        }

        public void Send<T>(T payload) where T : class
        {
            Type key = typeof(T);
            Log.DebugMessage(key.FullName);
            List<IEventAction> subscriberList = new List<IEventAction>();
            if (_actions.TryGetValue(key, out subscriberList))
            {
                subscriberList.ForEach(x =>
                {
                    x.Call(payload);
                });
            }
        }

        /// <summary>
        /// Global implementation
        /// </summary>
        /// <returns></returns>
        public static MessageBus Global()
        {
            if (_global == null)
                _global = new MessageBus();
            return _global;
        }
    }
}
