UI Transition Blueprint: Hyperspace Theme Toggle (Light <-> Dark)

CONTEXT:
We have two theme modes.
Light Mode: 30 SVG shapes bouncing around the screen using a JS requestAnimationFrame physics loop (DVD screensaver style).
Dark Mode: 60 CSS-animated lines fanning out from the center (warp speed effect).
We need a seamless transition between them using a "Smoke and Mirrors" approach by toggling CSS transitions on/off to override the JS physics.

REQUIREMENTS FOR AI AGENT:
Please implement the following state machine and DOM manipulation logic using our existing codebase structure. Use Refs for DOM manipulation to avoid React state lag during animations.

PHASE 1: LIGHT TO DARK (THE IMPLOSION)
When the user triggers Dark Mode, do not unmount immediately. Execute this sequence:
1. Pause the JS requestAnimationFrame physics loop for the 4 shapes.
2. Turn ON CSS transitions for the 4 shapes via inline styles (e.g., transition: all 0.5s cubic-bezier(0.4, 0, 1, 1)).
3. Update their inline styles to target the exact center of the screen (left: 50vw, top: 50vh) and squish them to nothing (transform: scale(0)).
4. Set a timeout for 500ms (matching the transition duration).
5. Once the timeout fires, update the theme state to Dark Mode (unmount Light shapes, mount Dark warp lines, fade background to black).

PHASE 2: DARK TO LIGHT (THE BIG BANG EJECTION)
When the user triggers Light Mode, we reverse the visual, shooting shapes outward before resuming physics.
1. Update the theme state to Light Mode.
2. On initial mount of the 4 shapes, force their starting position to the dead center (left: 50vw, top: 50vh), scale them to zero (transform: scale(0)), and turn ON CSS transitions (transition: all 0.5s ease-out).
3. Wait 1 frame (using setTimeout of 10ms or requestAnimationFrame) so the browser registers the center start position.
4. Update their inline styles to their new random starting coordinates (left: random X, top: random Y) and restore full size (transform: scale(1)). This triggers the visual explosion outward.
5. Set a timeout for 500ms.
6. Once the timeout fires, turn OFF CSS transitions completely (transition: none) to prevent physics stutter.
7. Assign initial velocities and start the JS requestAnimationFrame physics loop for the bouncing effect.

CRITICAL EDGE CASE HANDLING (MUST IMPLEMENT):

1. TRANSITION LOCK: The theme toggle button MUST be disabled during the 500ms transition windows. Introduce an `isTransitioning` state to prevent rapid double-clicking from overlapping the timeouts and breaking the DOM state.
2. STATE SYNC BEFORE rAF: In Phase 2, before resuming the JS physics loop, you MUST read the element's actual position after the CSS transition finishes. Update the JS physics coordinate refs (x, y) to match the DOM's current position so the shapes do not "jump" or snap to old coordinates when requestAnimationFrame takes over.
3. CLEANUP: All setTimeout calls used for the transition handoffs must be assigned to a ref and cleared in a useEffect cleanup block to prevent memory leaks if the component unmounts mid-animation.