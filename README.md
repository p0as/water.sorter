# water.sorter
I was bored of some offerwalls asking you to get to level gazillion on these water sort games so here you go
Feel free to shape this however you want or add more automacy to it since its manual for now

The search function used is a **BFS (Breadth-First Search)** so with too many prompts/bottles it may take more than a minute to go through all uninformed routes
You can add a heuristic approach to fixing this but i was too lazy to implement it{

# Functionality
Pygame based water sort puzzle solver, it transforms the pygame inputs into a key (special code) that can be decoded by the algorithm, heres how to use it:
1. Select the ammount of bottles (bottles in your water sort game) and levels (ammount of colors eeach bottle holds)
2. After that you need to build how your water sort level is with the help fo the explicitly stated instructions inside the code
3. After you build your water sort level it will transform that into the special code and decode it

# Cautions: Either putting way too many bottles, too many colors, or placing the colors with nonsensical syntax will result in it not functioning correctly, also if the level is too long it will take a while to decode.

# Happy coding!
