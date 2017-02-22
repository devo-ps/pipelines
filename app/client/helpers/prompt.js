export function processPromptDef(promptDef) {
 var ret = {};
 promptDef = promptDef || {};
 Object.keys(promptDef).map(function(key){
   if (prompt_def[key] === null){
         prompt_def[key] = ''
   }
   if (typeof promptDef[key] === 'string'){
     ret[key] = promptDef[key];
   } else if(prompt_def[key]['type'] == 'checkbox'){
     ret[key] = prompt_def[key]['default'] || false;
   } else if(prompt_def[key]['type'] == 'select'){
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
