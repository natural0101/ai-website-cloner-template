# Thematic reference map

## Direct / domain references

### Chipotle Order

- URL: https://www.chipotle.com/order/find-a-chipotle
- Access: live.
- Closeness: food ordering, pickup/delivery, location-dependent fulfillment.
- Relevant because: commercial journey starts by resolving how and where the order will be fulfilled.
- Borrow: explicit pickup/delivery choice, address/location task above marketing content.
- Transform: local address formats, zones, store hours and Russian copy if the target market is RU.
- Do not copy: imagery, campaign, typography, exact page composition.
- Section: first viewport and location gate.
- Risk: location permission failure; always support typed address.

### Domino’s Menu

- URL: https://www.dominos.com/pages/order/menu
- Access: live.
- Closeness: pizza categories, build-your-own choices, local availability.
- Relevant because: exposes a real modifier-heavy product model.
- Borrow: category clarity and explicit size/crust/sauce/topping dimensions.
- Transform: modifiers into backend-defined groups with min/max and delta price.
- Do not copy: coupons, proprietary UI/code, menu content.
- Section: menu and product configurator.
- Risk: combinatorial complexity; validate accessibility, invalid combinations and repricing.

### Fresha Booking Journey

- URL: https://www.fresha.com/help-center/knowledge-base/online-profile/101646-learn-how-clients-book-appointments-online
- Access: live.
- Closeness: service, specialist, real-time availability, booking review.
- Relevant because: documents the exact transactional order of decisions.
- Borrow: service-first flow, optional provider, availability, final review.
- Transform: reduce marketplace layers for one local business.
- Do not copy: business claims, screenshots, marketplace UI.
- Section: booking funnel.
- Risk: availability race; implement hold/expiry/retry.

## Adjacent / thematic references

### Booksy

- URL: https://booksy.com/en-gb
- Access: live.
- Closeness: local services, portfolio, verified reviews, appointment management.
- Borrow: connect proof and availability to the decision; expose reschedule/cancel.
- Transform: use the business’s real policies and data.
- Do not copy: app-first acquisition or marketplace density.
- Section: trust, service listing, manage booking.
- Risk: fake review migration; source and count must be real.

### Baymard Past Purchases

- URL: https://baymard.com/blog/grocery-food-delivery-orders
- Access: live.
- Closeness: repeat grocery/restaurant purchase behavior.
- Borrow: returning-user reorder close to the top.
- Transform: server revalidate every item, modifier, price and location.
- Do not copy: a history block for anonymous/new users.
- Section: returning home.
- Risk: stale menu and privacy.

## Visual / aesthetic references

### Allbirds Shop

- URL: https://www.allbirds.com/shop
- Access: live.
- Closeness: product-led hierarchy, category navigation, restrained merchandising.
- Borrow: clear assortment structure and consistent product emphasis.
- Transform: attributes and density to actual category.
- Do not copy: sustainability narrative, product photos, exact navigation.
- Section: header/category.
- Risk: oversized mega-nav; verify mobile and keyboard.

### Fresha Home

- URL: https://www.fresha.com/
- Access: live.
- Closeness: service discovery and time/location intent.
- Borrow: hero is an action frame, not only a slogan.
- Transform: for one business, remove unnecessary marketplace search dimensions.
- Do not copy: counters, testimonials, photos.
- Section: booking hero.
- Risk: unsupported social proof.

### Chipotle Order Campaign + Task

- URL: https://www.chipotle.com/order/find-a-chipotle
- Access: live.
- Closeness: expressive food brand surrounding an operational selector.
- Borrow: separate bold campaign imagery from clear functional controls.
- Transform: keep the selector within first viewport.
- Do not copy: seasonal assets or copy.
- Section: pizzeria hero and campaign block.
- Risk: visual campaign overwhelms order task.

## Motion / component references

### Motion Layout Animation

- URL: https://motion.dev/docs/react-layout-animations
- Access: live.
- Closeness: filter/list/cart state reflow.
- Borrow: short transform-based movement to preserve spatial understanding.
- Transform: duration, easing and reduced-motion fallback.
- Do not copy: app-store showcase transitions in transactional screens.
- Section: filters, cart, selected state.
- Risk: bundle, distortion, INP; verify on low-end mobile.

### Motion AnimatePresence

- URL: https://motion.dev/docs/react-animate-presence
- Access: live.
- Closeness: add/remove cart lines and drawers.
- Borrow: exit feedback only where it explains removal.
- Transform: focus restoration, ARIA announcement and undo.
- Do not copy: long choreography or waiting mode in checkout.
- Section: cart, product drawer, confirmation toast.
- Risk: delayed removal and lost focus.

## Flow reference

### Page Flows / Grab ordering food

- URL: https://pageflows.com/post/ios/ordering-food/grab/
- Access: public index, full flow account/premium gated.
- Closeness: categories, location, restaurant, item options, basket, order and success.
- Borrow: step inventory for flow and QA coverage.
- Transform: direct restaurant ordering, web responsive patterns.
- Do not copy: gated media, mobile app chrome, brand assets.
- Section: end-to-end flow map.
- Risk: incomplete access; screenshot evidence unavailable without account.
