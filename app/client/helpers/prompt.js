export function processPromptDef(promptDef) {
 var ret = {};
 promptDef = promptDef || {};
 Object.keys(promptDef).map(function(key){
   if (promptDef[key] === null){
    promptDef[key] = ''
   }
   if (typeof promptDef[key] === 'string'){
     ret[key] = promptDef[key];
   } else if(promptDef[key]['type'] == 'checkbox'){
     ret[key] = promptDef[key]['default'] || false;
   } else if(promptDef[key]['type'] == 'select'){
     if (promptDef[key]['default']){
       // Take default
       ret[key] = promptDef[key]['default'];
     } else {
       if (Object.keys(promptDef[key]).length > 0){
         // Take first
         ret[key] = promptDef[key]['options'][0];
       } else {
         // Make empty
         ret[key] = '';
       }
     }
   }
 })
 return ret;
}
