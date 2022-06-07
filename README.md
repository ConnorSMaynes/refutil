# RefUtil

## Summary

There is a fairly common need to reference some data in the callback of a weakref when the object is being garbage collected. This package provides an simple interface for creating new annotated, slotted, refererence types, which subclass weakref.ref in the standard library.

## Supported Systems

- Python 2.5+
- Linux
- Windows

## Examples

### Example 1 - Code

```python
import collections

import refutil


Subscription = collections.namedtuple('Subscription', ['callback', 'topic', 'subscription_id'])
SubscriptionWeakRef = refutil.reftype('SubscriptionWeakRef', ['subscription_id'])


class Subscriptions:

	def __init__(self):
		self.subscriptions = {}
	
	def _weak_remove_callback(self, ref):
		print('weak callback triggered')
		self.remove(ref.subscription_id)

	def add(self, topic, callback, subscription_id):
		# make a weak reference to the callback, so that it will be garbage
		# collected, but store the subscription_id in the reference
		# and then add a method callback, which will be weakly referenced as well,
		# to handle when the callback is garbage collected
		wrcallback = SubscriptionWeakRef(
				callback, 
				self._weak_remove_callback,
				subscription_id=subscription_id
			)
		subscription = Subscription(
				topic=topic, 
				callback=wrcallback, 
				subscription_id=subscription_id
			)
		self.subscriptions[subscription_id] = subscription
		print('subscription added', subscription_id)
	
	def remove(self, subscription_id):
		print('subscription removed', subscription_id)
		del self.subscriptions[subscription_id]


subs = Subscriptions()

def my_callback():
	pass

subs.add('topic', my_callback, 'sub-1')
subs.add('topic', my_callback, 'sub-2')

print(subs.subscriptions)

print('deleting callback')
del my_callback

print(subs.subscriptions)
```

### Example 1 - Output

```text
subscription added sub-1
subscription added sub-2
{'sub-1': Subscription(callback=<weakref at 0x01874300; to 'function' at 0x01873C48 (my_callback)>, topic='topic', subscription_id='sub-1'), 'sub-2': Subscription(callback=<weakref at 0x018743F0; to 'function' at 0x01873C48 (my_callback)>, topic='topic', subscription_id='sub-2')}        
deleting callback
weak callback triggered
subscription removed sub-2
weak callback triggered
subscription removed sub-1
{}
```
