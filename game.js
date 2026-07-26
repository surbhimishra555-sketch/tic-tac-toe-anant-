const menu = document.getElementById("menu");
const game = document.getElementById("game");
const board = document.getElementById("board");
const statusText = document.getElementById("status");

const PLAYER = "😈";
const AI = "😇";

let aiMode = false;
let current = PLAYER;
let active = true;
let state = Array(9).fill("");

const wins = [
  [0,1,2],[3,4,5],[6,7,8],
  [0,3,6],[1,4,7],[2,5,8],
  [0,4,8],[2,4,6]
];

function startPvP(){
    aiMode=false;
    startGame();
}
function startAI(){
    aiMode=true;
    startGame();
}

function startGame(){
    menu.style.display="none";
    game.style.display="block";
    init();
}

function restartGame(){
    init();
}

function init(){
    board.innerHTML="";
    state.fill("");
    active=true;
    current=PLAYER;
    statusText.textContent=`Player ${PLAYER} turn`;

    for(let i=0;i<9;i++){
        const cell=document.createElement("div");
        cell.className="cell";
        cell.onclick=()=>makeMove(cell,i);
        board.appendChild(cell);
    }
}

function makeMove(cell,i){
    if(!active || state[i]) return;

    state[i]=current;
    cell.textContent=current;

    if(checkWin(current)){
        statusText.textContent=`${current} wins 🎉`;
        active=false;
        return;
    }

    if(!state.includes("")){
        statusText.textContent="Draw 😐";
        active=false;
        return;
    }

    if(aiMode){
        current = current===PLAYER ? AI : PLAYER;
        statusText.textContent = current===AI ? "AI thinking 🤖..." : `Player ${PLAYER} turn`;

        if(current===AI){
            setTimeout(aiMove,500);
        }
    }else{
        current = current===PLAYER ? AI : PLAYER;
        statusText.textContent=`Player ${current} turn`;
    }
}

function aiMove(){
    if(!active) return;

    let bestScore = -Infinity;
    let move;

    for(let i=0;i<9;i++){
        if(state[i]==""){
            state[i]=AI;
            let score = minimax(state,0,false);
            state[i]="";
            if(score>bestScore){
                bestScore=score;
                move=i;
            }
        }
    }

    document.querySelectorAll(".cell")[move].click();
}

function minimax(boardState,depth,isMax){
    if(checkWinner(AI)) return 10-depth;
    if(checkWinner(PLAYER)) return depth-10;
    if(!boardState.includes("")) return 0;

    if(isMax){
        let best=-Infinity;
        for(let i=0;i<9;i++){
            if(boardState[i]==""){
                boardState[i]=AI;
                best=Math.max(best,minimax(boardState,depth+1,false));
                boardState[i]="";
            }
        }
        return best;
    }else{
        let best=Infinity;
        for(let i=0;i<9;i++){
            if(boardState[i]==""){
                boardState[i]=PLAYER;
                best=Math.min(best,minimax(boardState,depth+1,true));
                boardState[i]="";
            }
        }
        return best;
    }
}

function checkWin(player){
    return wins.some(w=>{
        const[a,b,c]=w;
        if(state[a]==player && state[b]==player && state[c]==player){
            document.querySelectorAll(".cell")[a].classList.add("win");
            document.querySelectorAll(".cell")[b].classList.add("win");
            document.querySelectorAll(".cell")[c].classList.add("win");
            return true;
        }
    });
}

function checkWinner(player){
    return wins.some(w=>{
        const[a,b,c]=w;
        return state[a]==player && state[b]==player && state[c]==player;
    });
}

if (typeof module !== "undefined" && module.exports) {
    module.exports = {
        startPvP, startAI, startGame, restartGame, init,
        makeMove, aiMove, minimax, checkWin, checkWinner, wins,
        getState: () => state,
    };
}
